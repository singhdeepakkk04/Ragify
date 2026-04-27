<div align="center">
  <img src="frontend/public/logo.svg" alt="RAGify Logo" width="120" height="120" />
  <h1>🚀 RAGify</h1>
  <p><b>The Production-Grade Multi-Tenant RAG Platform</b></p>

  <p>
    <img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" alt="FastAPI" />
    <img src="https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white" alt="Next.js" />
    <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL" />
    <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker" />
    <img src="https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white" alt="Supabase" />
  </p>

  <h4>"Upload documents → REST endpoint → Natural language answers with citations"</h4>
</div>

---

## ✨ Overview

**RAGify** is a multi-tenant, production-ready SaaS platform that simplifies the deployment of high-performance RAG (Retrieval-Augmented Generation) pipelines. It handles the complexity of PDF/image parsing, semantic chunking, dual-layer authentication, and hybrid search, providing you with a clean API to query your data.

## 🔥 Key Features

- **🌐 Multi-Tenant Architecture** — Full data isolation at the database, cache, and API layers using scoped project IDs.
- **🧠 Intelligent Query Planning** — LLMs analyze query intent to dynamically plan execution stages and select optimal models.
- **🔍 Hybrid Vector Search** — Combines `pgvector` Cosine Similarity with state-of-the-art BM25 keyword search using Reciprocal Rank Fusion (RRF).
- **🖼️ Vision-Powered Parsing** — Automatically extract text and context from Images and PDFs using Gemini Vision models.
- **⚡ Streaming NDJSON** — Instant response feedback with token-by-token streaming and real-time citation rendering.
- **📊 Production Monitoring** — Deep visibility into LLM performance and costs via built-in Langfuse tracing.
- **📏 Automated Evaluation** — Integrated Ragas/Eval framework to validate the correctness and groundedness of every response.

## 🛠️ Tech Stack

### Backend & AI
- **Framework:** FastAPI (Python 3.11)
- **Database:** PostgreSQL 16 + `pgvector`
- **Search:** Hybrid (Vector + Keyword) + Cohere Reranking
- **LLM Registry:** OpenAI, Groq, DeepSeek, Google Gemini, Sarvam
- **Cache:** Unified Dockerized Redis 7 (Local)

### Frontend
- **Framework:** Next.js 16 (App Router) + React 19
- **Styling:** Tailwind CSS v4 + Framer Motion
- **UI Components:** Shadcn/UI (Radix Primitives)
- **State Management:** Zustand + React Query

## 🚀 Getting Started

1. **Clone & Setup Environment**
   ```bash
   git clone https://github.com/singhdeepakkk04/Ragify.git
   cd Ragify
   cp .env.example .env
   ```

2. **Launch Infrastructure**
   ```bash
   # Starts PostgreSQL (pgvector) and Redis in Docker
   bash scripts/start_dev.sh
   ```

3. **Access Services**
   - **Frontend:** [http://localhost:3000](http://localhost:3000)
   - **Backend API:** [http://localhost:8000](http://localhost:8000)
   - **Interactive Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

## 📁 Repository Structure

```text
├── backend/            # FastAPI Application & Unit/Integration Tests
├── frontend/           # Next.js Dashboard & Playground
├── infrastructure/     # Docker Compose, Nginx Config & Terraform
├── scripts/            # Admin tools and Dev automation
├── docs/               # Architecture, Security & Runbooks
├── sdks/python/        # Official Python Client Library
└── supabase/           # SQL Migrations for Auth & RLS
```

## 🛡️ Security & Quality

RAGify is built with a focus on enterprise security:
- **Dual-Layer Auth:** Supabase JWT for web users + SHA-256 hashed API Keys for external apps.
- **Pre-commit Integrity:** Automated linting (Ruff), type checking (Mypy), and secret scanning (Gitleaks).
- **CI/CD:** Automated testing pipelines via GitHub Actions.

## 📄 License

This project is licensed under the **MIT License**.

---

<div align="center">
  <sub>Built with ❤️ by the RAGify Team</sub>
</div>
