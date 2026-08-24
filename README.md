# GenFlow AI

Enterprise AI content generation and automation platform with agentic workflows, RAG, prompt experiments, evaluation, caching, and a React dashboard.

## Features

- Multi-step content generation with validation and refinement.
- OpenAI and Anthropic provider abstraction.
- RAG over knowledge documents.
- Prompt versioning and evaluation-ready architecture.
- Redis response caching.
- PostgreSQL persistence.
- React monitoring/generation workspace.
- Docker Compose for local infrastructure.
- GitHub Actions CI.

## Quick start

```bash
cp .env.example .env
# Configure OPENAI_API_KEY or ANTHROPIC_API_KEY

docker compose up -d postgres redis
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

API docs: http://localhost:8000/docs
Frontend: http://localhost:5173

## Architecture

```text
React Dashboard
      |
   FastAPI
      |
 Content Agent ---- Prompt Registry
      |                    |
      +---- RAG ----------+---- Evaluator
      |                         |
    Redis                    Postgres
      |
 OpenAI / Anthropic
```
