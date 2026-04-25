# RAGify — Architecture Report

**Date:** 7 March 2026  
**Version:** 0.1.0  
**Author:** GitHub Copilot Architecture Review

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [High-Level Architecture Diagram](#2-high-level-architecture-diagram)
3. [Technology Stack](#3-technology-stack)
4. [Component Architecture](#4-component-architecture)
5. [Authentication & Authorization Flow](#5-authentication--authorization-flow)
6. [RAG Query Pipeline — Sequence Diagram](#6-rag-query-pipeline--sequence-diagram)
7. [Document Upload & Indexing Flow](#7-document-upload--indexing-flow)
8. [Data Model (Entity-Relationship Diagram)](#8-data-model-entity-relationship-diagram)
9. [API Surface Map](#9-api-surface-map)
10. [Infrastructure & Deployment Diagram](#10-infrastructure--deployment-diagram)
11. [Frontend Architecture](#11-frontend-architecture)
12. [Caching Architecture](#12-caching-architecture)
13. [Multi-Tenancy Design](#13-multi-tenancy-design)
14. [Data Flow: End-to-End Query](#14-data-flow-end-to-end-query)
15. [State Machine: Document Status](#15-state-machine-document-status)
16. [Key Design Decisions](#16-key-design-decisions)

---

## 1. System Overview

**RAGify** is a multi-tenant, production-ready SaaS platform that allows developers to build and deploy Retrieval-Augmented Generation (RAG) pipelines as managed REST API services.

**Core Value Proposition:**  
Upload your documents → Get a REST API endpoint → Query your documents in natural language with cited, grounded AI responses.

**Key Capabilities:**

| Capability | Description |
|---|---|
| Multi-tenancy | Full user/project isolation via denormalized `user_id`/`project_id` on every chunk |
| Hybrid Search | Vector (pgvector cosine) + Keyword (BM25 tsvector), fused with Reciprocal Rank Fusion |
| Query Expansion | LLM generates 3 query variations before retrieval to maximize recall |
| Reranking | Cohere cross-encoder reranking for precision improvement |
| Streaming | NDJSON streaming responses for low time-to-first-byte |
| Multi-provider LLM | OpenAI, Groq, Sarvam, DeepSeek, ZhipuAI — all via unified registry |
| Caching | Upstash Redis (30-min TTL) + in-memory LRU fallback |
| Observability | Langfuse LLM tracing for all pipeline stages |

---

## 2. High-Level Architecture Diagram

```mermaid
graph TB
    subgraph "Client Layer"
        Browser["🌐 Browser\n(Next.js Frontend)"]
        ExternalAPI["🔌 External API Consumer\n(API Key Auth)"]
    end

    subgraph "Identity Layer"
        Supabase["🔑 Supabase Auth\n(Email + Google OAuth)"]
    end

    subgraph "Application Layer"
        FastAPI["⚡ FastAPI Backend\n(Python 3.11 / uvicorn)"]
        
        subgraph "Middleware Stack"
            CORS["CORS Middleware"]
            AuthDep["Auth Dependency\n(JWT / API Key)"]
            RateLimit["Rate Limiter\n(Redis Sliding Window)"]
            Guardrails["Content Guardrails\n(Blocklist + Injection)"]
        end
    end

    subgraph "Data Layer"
        PG["🐘 PostgreSQL 16\n+ pgvector extension"]
        Redis["⚡ Redis 7\n(Rate Limits + Cache)"]
    end

    subgraph "AI / External Services"
        OpenAI["🤖 OpenAI API\n(Embeddings + GPT models)"]
        Cohere["🔄 Cohere API\n(Reranking)"]
        Groq["⚡ Groq\n(Fast LLM inference)"]
        Langfuse["📊 Langfuse\n(LLM Observability)"]
    end

    Browser -- "HTTPS + Supabase JWT" --> FastAPI
    ExternalAPI -- "X-API-Key header" --> FastAPI
    Browser -- "OAuth / Email Auth" --> Supabase
    Supabase -- "JWT issued to browser" --> Browser

    FastAPI --> PG
    FastAPI --> Redis
    FastAPI --> OpenAI
    FastAPI --> Cohere
    FastAPI --> Groq
    FastAPI --> Langfuse
```

---

## 3. Technology Stack

### Backend

| Layer | Technology | Purpose |
|---|---|---|
| Web Framework | FastAPI 0.109 | Async API, OpenAPI docs, dependency injection |
| ASGI Server | Uvicorn | HTTP/1.1 + HTTP/2 async server |
| ORM | SQLAlchemy 2.x (async) | DB model definitions, async queries |
| Migrations | Alembic | Database schema versioning |
| DB Driver | asyncpg | Async PostgreSQL driver |
| Vector Store | pgvector 0.7+ | 1536-dim vector storage + cosine similarity |
| Embeddings | OpenAI `text-embedding-3-small` | 1536-dimension dense embeddings |
| LLM Orchestration | LangChain | Prompt templates, chains, streaming |
| Reranking | Cohere `rerank-v3.5` | Cross-encoder re-ranking |
| Cache | Redis (Upstash) | Query result cache, TTL-based |
| Rate Limiting | Redis (docker local) | Sliding window per user |
| Auth Verification | PyJWT | JWT decode + HS256/ES256 verification |
| Password Hashing | passlib + bcrypt | Secure password storage |
| Tracing | Langfuse | LLM pipeline observability |
| Document Parsing | pypdf, python-docx | PDF and DOCX text extraction |
| Text Splitting | LangChain `RecursiveCharacterTextSplitter` | Chunk generation |

### Frontend

| Layer | Technology | Purpose |
|---|---|---|
| Framework | Next.js 16 (App Router) | SSR/SSG, routing, layouts |
| UI Library | React 19 | Component model |
| Language | TypeScript | Type safety |
| Styling | Tailwind CSS v4 | Utility-first CSS |
| Components | Shadcn/UI (Radix primitives) | Accessible UI components |
| Icons | Lucide React | Icon library |
| HTTP Client | Axios | API communication with interceptors |
| Auth State | Zustand | Single global auth store |
| Server State | TanStack React Query | API data fetching/caching |
| Forms | react-hook-form + Zod | Form validation |
| Charts | Recharts | Analytics dashboard |
| Auth Provider | Supabase Auth (JS SDK) | Email + Google OAuth |

### Infrastructure

| Component | Technology | Notes |
|---|---|---|
| Database | PostgreSQL 16 (pgvector/pgvector:pg16 image) | Vector + relational in one |
| Cache/Rate Limit | Redis 7 Alpine | Local Docker |
| Cloud Cache | Upstash Redis | Serverless Redis for query cache |
| Container Runtime | Docker Compose | Local/dev orchestration |
| Auth Service | Supabase | Managed auth (email, Google OAuth) |

---

## 4. Component Architecture

```mermaid
graph LR
    subgraph "backend/app/"
        direction TB

        subgraph "API Layer"
            main["main.py\n(FastAPI app + CORS)"]
            deps["api/deps.py\n(Auth middleware)"]
            router["api/api_v1/api.py\n(Router aggregator)"]
            
            subgraph "Endpoints"
                rag_ep["rag.py\n(POST /query)"]
                docs_ep["documents.py\n(upload/list/delete)"]
                proj_ep["projects.py\n(CRUD + API keys)"]
                usage_ep["usage.py\n(analytics)"]
                models_ep["models (in projects.py)"]
            end
        end

        subgraph "Core Logic"
            config["core/config.py\n(Settings via pydantic)"]
            security["core/security.py\n(bcrypt + JWT create)"]
            guardrails["core/guardrails.py\n(input/output sanitize)"]
            rate_limiter["core/rate_limiter.py\n(Redis sliding window)"]
            query_cache["core/query_cache.py\n(Redis/LRU cache)"]
            model_reg["core/model_registry.py\n(LLM catalog)"]
            tracing["core/tracing.py\n(Langfuse wrapper)"]
        end

        subgraph "RAG Pipeline"
            indexing["rag/indexing.py\n(chunk + embed + store)"]
            retrieval["rag/retrieval.py\n(query + stream)"]
            ingestion["rag/ingestion.py\n(legacy LangChain PGVector)"]
        end

        subgraph "Data Access"
            user_crud["crud/user.py"]
            proj_crud["crud/project.py"]
            doc_crud["crud/document.py"]
            key_crud["crud/apikey.py"]
        end

        subgraph "Models"
            user_model["models/user.py"]
            proj_model["models/project.py"]
            doc_model["models/document.py\n(DocumentChunk + Vector)"]
            key_model["models/apikey.py"]
            log_model["models/usage_log.py"]
        end

        subgraph "DB"
            session["db/session.py\n(AsyncSession factory)"]
            base["db/base.py\n(SQLAlchemy Base)"]
        end
    end

    main --> router
    router --> rag_ep & docs_ep & proj_ep & usage_ep
    rag_ep --> deps & guardrails & rate_limiter & retrieval & query_cache
    docs_ep --> deps & doc_crud & indexing & query_cache
    proj_ep --> deps & proj_crud & key_crud
    usage_ep --> deps
    retrieval --> model_reg & tracing & query_cache
    indexing --> session
    deps --> security
    proj_crud & doc_crud & user_crud & key_crud --> session
    session --> base
```

---

## 5. Authentication & Authorization Flow

```mermaid
sequenceDiagram
    participant Browser
    participant Supabase
    participant FastAPI
    participant DB as PostgreSQL

    rect rgb(240, 248, 255)
        Note over Browser,Supabase: User Login (Supabase Auth)
        Browser->>Supabase: POST /auth/v1/token (email + password)
        Supabase-->>Browser: JWT (HS256 or ES256)
        Browser->>Browser: Store JWT in Zustand AuthStore
    end

    rect rgb(240, 255, 240)
        Note over Browser,DB: JWT-Authenticated API Request
        Browser->>FastAPI: POST /api/v1/rag/query<br>Authorization: Bearer <JWT>
        FastAPI->>FastAPI: _decode_supabase_jwt(token)<br>1. Try HS256 with SUPABASE_JWT_SECRET<br>2. Fallback: Fetch JWKS → verify ES256
        FastAPI->>FastAPI: Extract email from payload
        FastAPI->>DB: SELECT * FROM users WHERE email = ?
        alt User exists
            DB-->>FastAPI: User record
        else User not found
            FastAPI->>DB: INSERT INTO users (auto-provision)
            DB-->>FastAPI: New user
        end
        FastAPI->>FastAPI: Verify project ownership
        FastAPI-->>Browser: Streaming NDJSON response
    end

    rect rgb(255, 248, 220)
        Note over Browser,DB: API Key Authentication (External Consumers)
        Browser->>FastAPI: POST /api/v1/rag/query<br>X-API-Key: rag_xxxxxxxxxxxx
        FastAPI->>FastAPI: SHA-256 hash the key
        FastAPI->>DB: SELECT * FROM api_keys WHERE key_hash = ?
        DB-->>FastAPI: APIKey record (project_id)
        FastAPI->>DB: SELECT * FROM projects WHERE id = ?<br>+ SELECT owner FROM users
        DB-->>FastAPI: Project + Owner user
        FastAPI->>FastAPI: Check API key scoped to requested project_id
        FastAPI-->>Browser: Streaming NDJSON response
    end
```

---

### Authorization Model

```mermaid
graph TD
    Request["Incoming Request"] --> AuthCheck{"Auth Type?"}
    
    AuthCheck -- "X-API-Key header" --> APIKeyFlow["Hash key → Lookup in DB"]
    AuthCheck -- "Bearer JWT" --> JWTFlow["Verify JWT → Extract email"]
    AuthCheck -- "Neither" --> Reject401["401 Unauthorized"]
    
    APIKeyFlow -- "Found + Active" --> GetOwner["Resolve key owner\n(project's owner_id)"]
    APIKeyFlow -- "Not Found" --> Reject401
    
    JWTFlow -- "Valid + Not Expired" --> GetUser["Lookup/create user\nby email"]
    JWTFlow -- "Invalid / Expired" --> Reject401
    
    GetOwner --> ScopeCheck{"API Key scoped\nto requested project?"}
    ScopeCheck -- "No" --> Reject403["403 Forbidden"]
    ScopeCheck -- "Yes" --> ActiveCheck
    
    GetUser --> ActiveCheck{"Is user active?"}
    ActiveCheck -- "No" --> Reject400["400 Inactive User"]
    ActiveCheck -- "Yes" --> RoleCheck
    
    RoleCheck{"Endpoint requires\nadmin?"}
    RoleCheck -- "Yes, user is admin" --> Proceed["✅ Proceed to handler"]
    RoleCheck -- "Yes, user is not admin" --> Reject403
    RoleCheck -- "No admin required" --> OwnerCheck

    OwnerCheck{"Endpoint requires\nresource ownership?"}
    OwnerCheck -- "Ownership verified" --> Proceed
    OwnerCheck -- "Not owner" --> Reject404["404 Not Found\n(ownership-aware 404)"]
```

---

## 6. RAG Query Pipeline — Sequence Diagram

```mermaid
sequenceDiagram
    participant Client
    participant API as FastAPI /rag/query
    participant Guard as Guardrails
    participant Cache as Query Cache
    participant Expand as Query Expansion (LLM)
    participant Search as Hybrid Search (PG)
    participant Rerank as Cohere Reranker
    participant LLM as LLM (streaming)
    participant Langfuse

    Client->>API: POST /rag/query {project_id, query, top_k}
    API->>Guard: check_input(query)
    Guard-->>API: sanitized_query / 400 if blocked

    API->>Cache: get(user_id, project_id, query)
    alt Cache HIT
        Cache-->>API: cached {answer, citations}
        API-->>Client: Stream cached answer + citations
    else Cache MISS
        Cache-->>API: None

        API->>Langfuse: trace.span("query_expansion")
        API->>Expand: expand_query(query) → GPT-3.5
        Expand-->>API: [original, alt1, alt2, alt3]

        API->>Langfuse: trace.span("hybrid_search")
        par Parallel for each query variation
            API->>Search: embed_query(q) → OpenAI
            Search-->>API: embedding vector
            API->>Search: Vector cosine search (pgvector <=>)
            API->>Search: BM25 keyword search (tsvector @@)
        end
        Search-->>API: All results (up to 4×top_k chunks)

        API->>API: RRF Fusion (Reciprocal Rank Fusion)\nDedup by chunk ID

        API->>Langfuse: trace.span("reranking")
        API->>Rerank: rerank(query, chunks, top_n=7)
        Rerank-->>API: reranked_chunks

        API-->>Client: Stream: {"citations": [...]}

        API->>Langfuse: trace.generation("llm_generation")
        loop Streaming tokens
            API->>LLM: stream(context + query)
            LLM-->>API: token
            API-->>Client: Stream: {"token": "..."}
        end

        API->>Cache: set(user_id, project_id, query, {answer, citations})
        API->>Langfuse: flush()
    end
```

---

## 7. Document Upload & Indexing Flow

```mermaid
sequenceDiagram
    participant User
    participant API as FastAPI /documents/upload
    participant BG as Background Task (FastAPI)
    participant Parser as File Parser
    participant Splitter as Text Splitter
    participant OpenAI
    participant DB as PostgreSQL

    User->>API: POST /documents/upload (multipart: file + project_id)
    
    API->>API: Verify project ownership (owner_id == current_user.id)
    API->>API: Check file size ≤ 20 MB
    
    alt file.endswith(".pdf")
        API->>Parser: pypdf.PdfReader → extract per-page text
    else file.endswith(".docx")
        API->>Parser: python-docx → extract paragraph text
    else file.endswith(".txt" | ".md")
        API->>Parser: decode UTF-8
    end
    
    Parser-->>API: pages = [{page: N, text: "..."}]
    
    API->>DB: INSERT INTO documents (filename, project_id, status=PENDING)
    DB-->>API: document_id
    
    API->>User: 200 OK {document_id, status: "pending"}
    Note over API,User: Response returned immediately — indexing is async
    
    API->>BG: add_task(index_document, doc_id, pages, project_id, user_id)
    
    BG->>DB: UPDATE documents SET status = 'processing'
    
    loop For each page
        BG->>Splitter: RecursiveCharacterTextSplitter(chunk_size=1000, overlap=200)
        Splitter-->>BG: [chunk1, chunk2, ...]
    end
    
    BG->>OpenAI: embeddings.create(model="text-embedding-3-small", input=all_chunks)
    Note over BG,OpenAI: Batched: 100 chunks per API call
    OpenAI-->>BG: [[float x 1536], ...] 
    
    loop For each chunk
        BG->>DB: INSERT INTO document_chunks<br>(content, embedding:Vector(1536),<br>user_id, project_id, page_number, chunk_metadata)
    end
    
    BG->>DB: UPDATE document_chunks<br>SET search_vector = to_tsvector('english', content)<br>WHERE project_id=? AND document_id=?
    Note over BG,DB: Populates tsvector for BM25 full-text search
    
    BG->>DB: UPDATE documents SET status = 'completed'
    
    BG->>BG: query_cache.invalidate_project(project_id)
    Note over BG: Clears stale cached answers for this project
```

---

## 8. Data Model (Entity-Relationship Diagram)

```mermaid
erDiagram
    USERS {
        int id PK
        string email UK
        string hashed_password
        boolean is_active
        string role
        datetime created_at
    }

    PROJECTS {
        int id PK
        string name
        string description
        string project_type
        string llm_model
        string embedding_model
        float temperature
        int chunk_size
        int chunk_overlap
        int top_k
        string deployment_environment
        boolean is_public
        json config
        datetime created_at
        int owner_id FK
    }

    DOCUMENTS {
        int id PK
        int project_id FK
        string filename
        text content
        string status
        datetime created_at
    }

    DOCUMENT_CHUNKS {
        int id PK
        int document_id FK
        int user_id
        int project_id
        text content
        vector_1536 embedding
        int chunk_index
        int page_number
        json chunk_metadata
        tsvector search_vector
    }

    API_KEYS {
        int id PK
        int project_id FK
        string key_hash UK
        string prefix
        string name
        boolean is_active
        datetime created_at
    }

    USAGE_LOGS {
        int id PK
        int user_id FK
        int project_id FK
        text query
        string model_used
        int tokens_used
        float latency_ms
        datetime created_at
    }

    USERS ||--o{ PROJECTS : "owns"
    PROJECTS ||--o{ DOCUMENTS : "contains"
    DOCUMENTS ||--o{ DOCUMENT_CHUNKS : "split into"
    PROJECTS ||--o{ API_KEYS : "has"
    USERS ||--o{ USAGE_LOGS : "generates"
    PROJECTS ||--o{ USAGE_LOGS : "tracked in"
```

### Denormalization Note

`DOCUMENT_CHUNKS` intentionally stores `user_id` and `project_id` directly (denormalized from the `PROJECTS` → `USERS` relationship). This is a deliberate performance optimization: every retrieval query filters on `WHERE user_id = ? AND project_id = ?` without requiring any JOIN, reducing retrieval latency at scale.

---

## 9. API Surface Map

```mermaid
graph LR
    subgraph "Public"
        root["GET /\n(health check)"]
    end

    subgraph "Auth Required (/api/v1)"
        subgraph "Projects"
            p1["POST /projects"]
            p2["GET /projects"]
            p3["GET /projects/{id}"]
            p4["PATCH /projects/{id}"]
            p5["DELETE /projects/{id}"]
            p6["GET /projects/{id}/api-key"]
            p7["POST /projects/{id}/api-key/regenerate"]
            p8["GET /projects/models"]
        end

        subgraph "Documents"
            d1["POST /documents/upload"]
            d2["GET /documents?project_id="]
            d3["DELETE /documents/{id}"]
        end

        subgraph "RAG"
            r1["POST /rag/query\n(rate limited)"]
            r2["GET /rag/cache/stats"]
        end

        subgraph "Usage"
            u1["GET /usage/"]
        end
    end

    r1 -- "API Key\nor JWT" --> r1
    p1 & p2 & p3 & p4 & p5 & p6 & p7 & p8 -- "JWT only" --> p1
    d1 & d2 & d3 -- "JWT only" --> d1
    u1 -- "JWT only" --> u1
```

### Endpoint Reference Table

| Method | Path | Auth | Rate Limited | Streaming |
|--------|------|------|-------------|-----------|
| `GET` | `/` | None | No | No |
| `POST` | `/api/v1/projects` | JWT | No | No |
| `GET` | `/api/v1/projects` | JWT | No | No |
| `GET` | `/api/v1/projects/{id}` | JWT | No | No |
| `PATCH` | `/api/v1/projects/{id}` | JWT | No | No |
| `DELETE` | `/api/v1/projects/{id}` | JWT | No | No |
| `GET` | `/api/v1/projects/{id}/api-key` | JWT | No | No |
| `POST` | `/api/v1/projects/{id}/api-key/regenerate` | JWT | No | No |
| `GET` | `/api/v1/projects/models` | JWT | No | No |
| `POST` | `/api/v1/documents/upload` | JWT | No | No |
| `GET` | `/api/v1/documents` | JWT | No | No |
| `DELETE` | `/api/v1/documents/{id}` | JWT | No | No |
| `POST` | `/api/v1/rag/query` | JWT or API Key | ✅ 10/min | ✅ NDJSON |
| `GET` | `/api/v1/rag/cache/stats` | JWT | No | No |
| `GET` | `/api/v1/usage/` | JWT | No | No |

---

## 10. Infrastructure & Deployment Diagram

```mermaid
graph TB
    subgraph "Developer Machine / Server"
        subgraph "Docker Compose"
            PG["📦 ragify-db\npgvector/pgvector:pg16\nPort: 5432"]
            Redis["📦 ragify-redis\nredis:7-alpine\nPort: 6379"]
            PGVol["💾 postgres_data\n(Docker volume)"]
            RedisVol["💾 redis_data\n(Docker volume)"]
        end
        
        subgraph "Native Process (no container)"
            Backend["🐍 FastAPI Backend\nuvicorn app.main:app\nPort: 8000"]
            Frontend["⚛️ Next.js Dev Server\nnpm run dev\nPort: 3000"]
        end

        PG --> PGVol
        Redis --> RedisVol
        Backend --> PG
        Backend --> Redis
    end

    subgraph "Cloud Services"
        Supabase["☁️ Supabase\n(Auth only in local mode)"]
        UpstashRedis["☁️ Upstash Redis\n(Query Cache)"]
        OpenAICloud["☁️ OpenAI API\n(Embeddings + GPT)"]
        CohereCloud["☁️ Cohere API\n(Reranking)"]
        LangfuseCloud["☁️ Langfuse Cloud\n(Tracing)"]
    end

    Browser["🌐 Browser"] --> Frontend
    Frontend --> Backend
    Backend --> Supabase
    Backend --> UpstashRedis
    Backend --> OpenAICloud
    Backend --> CohereCloud
    Backend --> LangfuseCloud
```

### Deployment Notes

- The backend and frontend are **not containerized** in the current `docker-compose.yml` — only infrastructure services (PostgreSQL, Redis) are.
- For production, the backend should be containerized and placed behind an Nginx/Caddy/Traefik reverse proxy for TLS termination.
- Alembic migrations must be run before the backend starts: `alembic upgrade head`

---

## 11. Frontend Architecture

```mermaid
graph TB
    subgraph "Next.js App Router Layout"
        RootLayout["layout.tsx\n(Providers: QueryClient, AuthInit)"]
        
        subgraph "Route Groups"
            AuthGroup["(auth)/layout.tsx\n(Public: login/signup)"]
            DashboardGroup["(dashboard)/layout.tsx\n(Protected: sidebar + nav)"]
            AdminGroup["admin/\n(Admin panel)"]
        end
        
        subgraph "Pages"
            LoginPage["login/page.tsx"]
            SignupPage["signup/page.tsx"]
            DashboardPage["dashboard/page.tsx\n(project list + usage stats)"]
            AdminPage["admin/page.tsx"]
        end

        subgraph "Components"
            SurveyForm["project-wizard/SurveyForm.tsx\n(project creation wizard)"]
            UIComponents["ui/\n(shadcn: button, card, dialog, etc.)"]
        end
    end

    subgraph "State Management"
        AuthStore["Zustand AuthStore\n(user, session, isAuthenticated)"]
        ReactQuery["TanStack Query\n(API data, mutations)"]
    end

    subgraph "API/Auth Layer"
        AxiosClient["lib/api.ts\n(axios + JWT interceptor)"]
        AuthLib["lib/auth.ts\n(Zustand store definition)"]
        SupabaseClient["lib/supabase.ts\n(createClient wrapper)"]
        RecommendationEngine["lib/recommendationEngine.ts\n(project type suggestions)"]
    end

    RootLayout --> AuthGroup & DashboardGroup & AdminGroup
    AuthGroup --> LoginPage & SignupPage
    DashboardGroup --> DashboardPage
    LoginPage & SignupPage -- "auth actions" --> SupabaseClient
    DashboardPage --> SurveyForm
    DashboardPage --> ReactQuery
    ReactQuery --> AxiosClient
    AxiosClient -- "reads token" --> AuthStore
    AuthStore --> SupabaseClient
```

---

## 12. Caching Architecture

```mermaid
graph LR
    subgraph "Query Cache (RedisQueryCache)"
        direction TB
        
        CacheKey["Cache Key\nSHA-256( user_id:project_id:normalized_query )"]
        
        subgraph "Redis (Upstash)"
            CacheEntry["ragify:cache:{sha256}\n(TTL: 30 min)"]
            ProjMapping["ragify:proj:{project_id}:{cache_key}\n(for invalidation, TTL: 30 min)"]
        end
        
        subgraph "Fallback: In-Memory LRU"
            LRUCache["OrderedDict\n(max 500 entries, 30 min TTL)"]
        end
    end

    subgraph "Invalidation Triggers"
        UploadDoc["Document Uploaded\n→ invalidate_project(project_id)"]
        DeleteDoc["Document Deleted\n→ invalidate_project(project_id)"]
    end

    subgraph "Cache Operations"
        GET["GET: user_id + project_id + query\n→ hash key → Redis GET\n→ fallback LRU on Redis fail"]
        SET["SET: store answer + citations\n+ register under project key\nfor future invalidation"]
        INVALIDATE["INVALIDATE: SCAN ragify:proj:{pid}:*\n→ DELETE all matching cache keys"]
    end

    UploadDoc & DeleteDoc --> INVALIDATE
    INVALIDATE --> ProjMapping & CacheEntry
```

### Cache Key Design

The cache key is a SHA-256 hash of `"{user_id}:{project_id}:{normalized_query}"`. This guarantees:

1. **Cross-user isolation**: User A cannot read User B's cached answers
2. **Cross-project isolation**: Querying project 1 and project 2 with the same text produces separate cache entries
3. **Query normalization**: `query.lower().strip()` is applied before hashing — minor case/whitespace differences still produce cache hits

---

## 13. Multi-Tenancy Design

```mermaid
graph TB
    subgraph "Tenant: User A"
        UA["User A (id=1)"]
        PA1["Project A1 (id=10)"]
        PA2["Project A2 (id=11)"]
        DA1["Documents in A1"]
        CA1["Chunks: user_id=1\nproject_id=10"]
    end

    subgraph "Tenant: User B"
        UB["User B (id=2)"]
        PB1["Project B1 (id=20)"]
        DB1["Documents in B1"]
        CB1["Chunks: user_id=2\nproject_id=20"]
    end

    UA --> PA1 & PA2
    PA1 --> DA1 --> CA1
    UB --> PB1
    PB1 --> DB1 --> CB1

    subgraph "Isolation Enforcement"
        VecSQL["Vector Search SQL:\nWHERE user_id = :user_id\n  AND project_id = :project_id"]
        BM25SQL["BM25 Search SQL:\nWHERE user_id = :user_id\n  AND project_id = :project_id"]
    end

    CA1 & CB1 -.-> VecSQL & BM25SQL
    Note["⚠️ Both searches always filter\non BOTH user_id AND project_id.\nNo cross-tenant leakage possible\neven if project_id is guessed."]
```

**Tenancy Isolation Layers:**

| Layer | Isolation Mechanism |
|---|---|
| Database | `WHERE user_id = ? AND project_id = ?` on every chunk retrieval |
| API | `project.owner_id != current_user.id` → 404 |
| Cache | Cache key includes `user_id` |
| API Keys | Key scoped to one project_id; verified in request |
| Supabase RLS | Row-level policies on projects/documents tables |

---

## 14. Data Flow: End-to-End Query

```mermaid
flowchart TD
    A["User submits query\n'What are my tax deductions?'"] --> B["FastAPI receives\nPOST /rag/query"]
    B --> C{"Rate limit\nexceeded?"}
    C -- "Yes" --> C1["429 Too Many Requests"]
    C -- "No" --> D{"Input\nGuardrail"}
    D -- "Blocked" --> D1["400 Bad Request\n(policy violation)"]
    D -- "Pass" --> E{"Cache\nHit?"}
    E -- "HIT" --> E1["Stream cached answer\n(~50ms)"]
    E -- "MISS" --> F["Query Expansion\n(LLM: 3 alternatives)"]
    F --> G["Parallel Embedding\n4 queries × OpenAI API"]
    G --> H["Parallel DB Search\n4× vector + 4× BM25"]
    H --> I["RRF Fusion\n+ Deduplication"]
    I --> J["Cohere Reranking\n20 chunks → 7 best"]
    J --> K["Stream Citations\n{citations: [...]}"]
    K --> L["LLM Generation\nGPT / Groq / Sarvam\n(streaming tokens)"]
    L --> M["Stream token chunks\n{token: '...'}"]
    M --> N["Cache result\n(TTL: 30 min)"]
    N --> O["Log to usage_logs\n(latency, model, query)"]
    O --> P["Send traces\nto Langfuse"]
```

---

## 15. State Machine: Document Status

```mermaid
stateDiagram-v2
    [*] --> PENDING : POST /documents/upload\n(DB record created)

    PENDING --> PROCESSING : Background task starts\n(index_document called)
    
    PROCESSING --> COMPLETED : All chunks indexed,\nembeddings stored,\ntsvector populated

    PROCESSING --> FAILED : Exception during parsing,\nembedding, or DB write

    FAILED --> [*] : Document remains in DB\n(user can retry by re-uploading)
    COMPLETED --> [*] : Document queryable\nvia RAG pipeline

    note right of PENDING
        Document record exists
        No chunks yet
        File text extracted
    end note

    note right of PROCESSING
        Chunks being created
        OpenAI API called
        Vectors being written
    end note

    note right of COMPLETED
        All chunks in DB
        search_vector populated
        Cache invalidated
    end note
```

---

## 16. Key Design Decisions

### Decision 1: Denormalized `user_id` / `project_id` on Chunks

**Context:** High-frequency retrieval queries must filter by user and project.  
**Decision:** Store `user_id` and `project_id` directly on the `document_chunks` table rather than resolving them via JOIN (`document_chunks → documents → projects → users`).  
**Rationale:** At 10+ queries/second across many tenants, a 3-table JOIN on the hot retrieval path adds non-trivial latency. Denormalization avoids this entirely.  
**Trade-off:** Data duplication; `user_id` must be correctly set at write time and never changes.

---

### Decision 2: Active Implementation is `indexing.py`, not `ingestion.py`

**Context:** Two RAG implementations exist: `ingestion.py` (LangChain `PGVector` abstraction) and `indexing.py` (raw SQLAlchemy + OpenAI calls).  
**Decision:** `indexing.py` is the production implementation.  
**Rationale:** LangChain's `PGVector` abstraction hides metadata storage, page number tracking, and chunk structure. The raw implementation gives full control over `page_number`, `chunk_metadata`, `user_id`, and `project_id` columns.  
**Trade-off:** More code to maintain; relies on internal OpenAI SDK directly.

---

### Decision 3: Dual Auth (JWT + API Key) at the Dependency Level

**Context:** Two types of consumers — frontend users (JWT) and external developers (API Key).  
**Decision:** Both auth types are resolved in `deps.py` before the endpoint handler runs. The handler operates on a `User` object regardless of how auth was performed.  
**Rationale:** Endpoints remain auth-mechanism-agnostic. Rate limiting and guardrails work identically for both auth types.  
**Trade-off:** API Key auth resolves the project owner as `current_user`, which requires the API key's project ownership check to happen before the pipeline runs.

---

### Decision 4: Streaming NDJSON vs Single JSON Response

**Context:** LLM generation can take 3–15 seconds for complex queries.  
**Decision:** Stream LLM tokens as NDJSON (`application/x-ndjson`) — each line is a complete JSON object.  
**Rationale:** Users see the first tokens within ~1 second, dramatically improving perceived performance.  
**Format:**
```json
{"citations": [{"filename": "...", "page": 1, "snippet": "..."}]}
{"token": "Based on your "}
{"token": "documents, the "}
{"token": "answer is..."}
```

---

### Decision 5: Reciprocal Rank Fusion over Score Normalization

**Context:** Hybrid search produces two ranked lists (vector cosine scores and BM25 TF-IDF scores) that are not directly comparable (different value ranges and semantics).  
**Decision:** Use Reciprocal Rank Fusion (RRF) with `k=60`.  
**Rationale:** RRF only cares about relative rank position, not absolute score — making it robust even when the two search modalities produce incomparable raw scores.  
**Formula:** `RRF_score(doc) = Σ 1 / (k + rank_in_list)`

---

### Decision 6: Background Task Indexing

**Context:** Indexing a document (parsing → chunking → embedding → storing) can take 10–60 seconds for large PDFs.  
**Decision:** Use FastAPI `BackgroundTasks` — the upload endpoint returns `200 OK` immediately with `status: "pending"`, and indexing runs asynchronously.  
**Rationale:** Document upload should never block the HTTP response. Users can poll the document status to see when it's ready.  
**Trade-off:** Users may query a project immediately after upload and get no results (document not yet indexed). A status polling endpoint or WebSocket would improve UX.

---

*Report generated by GitHub Copilot Architecture Review — 7 March 2026*
