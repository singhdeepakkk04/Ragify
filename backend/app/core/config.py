from pydantic_settings import BaseSettings
from pathlib import Path

# Resolve .env relative to this file's location (backend/app/core/config.py → project root)
_env_path = Path(__file__).resolve().parents[3] / ".env"

class Settings(BaseSettings):
    PROJECT_NAME: str = "RAGify"
    DATABASE_URL: str

    OPENAI_API_KEY: str = ""
    COHERE_API_KEY: str = ""
    SARVAM_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    DEEPSEEK_API_KEY: str = ""
    ZHIPUAI_API_KEY: str = ""
    # Redis URL for Docker Redis (used for both rate limiting and query caching)
    # If REDIS_PASSWORD is set in docker-compose, encode it here:
    # REDIS_URL=redis://:your_password@localhost:6379
    # Use rediss:// for TLS when available; see REDIS_VERIFY_SSL.
    REDIS_URL: str = "redis://localhost:6379"

    # Optional explicit auth/SSL settings when the URL is not sufficient
    REDIS_USERNAME: str = ""
    REDIS_PASSWORD: str = ""
    REDIS_VERIFY_SSL: bool = True

    # Docker Postgres vars (used by docker-compose, optional in Python context)
    POSTGRES_USER: str = ""
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""

    # Supabase JWT secret — used for local token verification (no Supabase network call needed)
    # Get from: Supabase Dashboard → Settings → API → JWT Secret
    SUPABASE_JWT_SECRET: str = ""
    # Legacy (kept for reference, not used for auth anymore)
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""

    # Langfuse — LLM Observability (Cloud)
    # Generate keys at: cloud.langfuse.com → Project Settings → API Keys
    LANGFUSE_PUBLIC_KEY: str = ""
    LANGFUSE_SECRET_KEY: str = ""
    LANGFUSE_HOST: str = "https://cloud.langfuse.com"

    # CORS allowed origins (comma-separated in env, e.g. CORS_ALLOWED_ORIGINS=http://localhost:3000,https://app.example.com)
    CORS_ALLOWED_ORIGINS: str = "http://localhost:3000"

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.CORS_ALLOWED_ORIGINS.split(",") if o.strip()]

    # Debug mode — controls SQL echo, verbose logging
    DEBUG: bool = False

    # Database SSL mode: "disable", "require", "verify-ca", "verify-full"
    # Use "disable" for local Docker, "require" or "verify-full" for production
    DB_SSL_MODE: str = "require"

    # Rate limits (per minute) and sliding window seconds for all routes
    RATE_LIMIT_RAG_PER_MIN: int = 10
    RATE_LIMIT_UPLOAD_PER_MIN: int = 5
    RATE_LIMIT_MUTATION_PER_MIN: int = 20
    RATE_LIMIT_DEFAULT_PER_MIN: int = 120
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    # Tenant quotas (0 = disabled)
    TENANT_DAILY_QUERY_LIMIT: int = 0

    # ── Query Planner (Ollama) ───────────────────────────────────────────────
    # Disabled by default — enable when a fast local LLM is available (GPU required)
    PLANNER_ENABLED: bool = False
    PLANNER_OLLAMA_URL: str = "http://localhost:11434"
    PLANNER_MODEL: str = "phi3:mini"
    PLANNER_TIMEOUT: float = 3.0        # seconds
    PLANNER_CACHE_TTL: int = 3600       # 1 hour

    class Config:
        env_file = str(_env_path)
        extra = "ignore"

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return self.DATABASE_URL

settings = Settings()
