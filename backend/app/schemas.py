from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    prompt: str = Field(min_length=3)
    provider: str | None = None
    use_rag: bool = True
    temperature: float = Field(default=0.4, ge=0, le=1)


class GenerateResponse(BaseModel):
    id: int
    output: str
    provider: str
    model: str
    quality_score: float
    latency_ms: int
    cached: bool


class FeedbackRequest(BaseModel):
    generation_id: int
    rating: int = Field(ge=1, le=5)
    comment: str = ""


class KnowledgeRequest(BaseModel):
    title: str
    content: str = Field(min_length=10)


class PromptCreate(BaseModel):
    name: str
    template: str = Field(min_length=5)


class EvaluationRequest(BaseModel):
    prompt: str
    output: str
