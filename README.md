# RAGify

Multi-tenant SaaS platform for production RAG pipelines.

Upload documents → get a REST endpoint → query in natural language with cited, grounded responses.

## Features

- Hybrid search — pgvector cosine + BM25, fused with RRF
- Multi-tenant isolation — user + project separation at every layer
- Streaming NDJSON — citations first, then token stream
- Multi-provider LLM — OpenAI, Groq, Sarvam, DeepSeek, ZhipuAI
- Cohere reranking
- Redis query cache with project-scoped invalidation
- Langfuse observability
- Dual auth — Supabase JWT (frontend) + API key (external consumers)

## Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI, Python 3.11, SQLAlchemy 2 async |
| Database | PostgreSQL 16 + pgvector |
| Cache | Redis 7 + Upstash |
| Frontend | Next.js 16, React 19, TypeScript, Tailwind v4, shadcn/ui |
| Auth | Supabase (email + Google OAuth) |

## Getting started

```bash
cp .env.example .env   # fill in OPENAI_API_KEY, SUPABASE_* values
bash scripts/start_dev.sh
```

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API docs: http://localhost:8000/docs

## Testing

```bash
cd backend && pytest tests/unit/ -v
cd frontend && npm test
```

## Structure
ragify/
├── backend/              FastAPI app + tests
├── frontend/             Next.js app
├── infrastructure/       docker-compose, nginx
├── scripts/              dev + admin scripts
├── docs/                 architecture, security, runbooks
├── supabase/             migrations
└── sdks/python/          Python SDK

## Docs

- [Architecture](docs/architecture.md)
- [Security](docs/security.md)
- [Contributing](CONTRIBUTING.md)

## License

MIT

