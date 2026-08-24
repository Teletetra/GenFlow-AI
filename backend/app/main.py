import time
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from .agent import agent
from .cache import get as cache_get, put as cache_put
from .config import settings
from .db import Base, engine, get_db
from .evaluator import evaluate_output
from .models import Feedback, Generation, PromptVersion
from .rag import retriever
from .schemas import (
    EvaluationRequest,
    FeedbackRequest,
    GenerateRequest,
    GenerateResponse,
    KnowledgeRequest,
    PromptCreate,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="GenFlow AI", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/v1/health")
def health():
    return {"status": "ok", "service": "genflow-api", "environment": settings.app_env}


@app.post("/api/v1/generate", response_model=GenerateResponse)
def generate(request: GenerateRequest, db: Session = Depends(get_db)):
    payload = request.model_dump()
    cached = cache_get(payload)
    if cached:
        return GenerateResponse(**cached, cached=True)

    start = time.perf_counter()
    try:
        output, provider, model, score = agent.run(
            request.prompt,
            request.provider,
            request.use_rag,
            request.temperature,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    latency = int((time.perf_counter() - start) * 1000)
    record = Generation(
        prompt=request.prompt,
        output=output,
        provider=provider,
        model=model,
        quality_score=score,
        latency_ms=latency,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    value = {
        "id": record.id,
        "output": output,
        "provider": provider,
        "model": model,
        "quality_score": score,
        "latency_ms": latency,
    }
    cache_put(payload, value)
    return GenerateResponse(**value, cached=False)


@app.get("/api/v1/generations")
def generations(db: Session = Depends(get_db)):
    rows = db.scalars(
        select(Generation).order_by(Generation.created_at.desc()).limit(50)
    ).all()
    return [
        {
            "id": row.id,
            "prompt": row.prompt,
            "output": row.output,
            "provider": row.provider,
            "model": row.model,
            "quality_score": row.quality_score,
            "latency_ms": row.latency_ms,
            "created_at": row.created_at.isoformat(),
        }
        for row in rows
    ]


@app.post("/api/v1/feedback")
def feedback(request: FeedbackRequest, db: Session = Depends(get_db)):
    row = Feedback(**request.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return {"id": row.id, "status": "recorded"}


@app.post("/api/v1/knowledge")
def knowledge(request: KnowledgeRequest):
    retriever.add(request.title, request.content)
    return {"status": "indexed", "title": request.title}


@app.post("/api/v1/evaluations")
def evaluate(request: EvaluationRequest):
    return {
        "quality_score": evaluate_output(request.prompt, request.output),
        "validation": "passed" if request.output.strip() else "failed",
    }


@app.post("/api/v1/prompts")
def create_prompt(request: PromptCreate, db: Session = Depends(get_db)):
    existing = db.scalars(
        select(PromptVersion)
        .where(PromptVersion.name == request.name)
        .order_by(PromptVersion.version.desc())
    ).first()
    version = (existing.version + 1) if existing else 1
    row = PromptVersion(name=request.name, version=version, template=request.template)
    db.add(row)
    db.commit()
    db.refresh(row)
    return {"id": row.id, "name": row.name, "version": row.version}


@app.get("/api/v1/prompts")
def list_prompts(db: Session = Depends(get_db)):
    rows = db.scalars(
        select(PromptVersion).order_by(PromptVersion.name, PromptVersion.version.desc())
    ).all()
    return [
        {"id": row.id, "name": row.name, "version": row.version, "template": row.template}
        for row in rows
    ]
