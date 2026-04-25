from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# SEC-11: Configurable SSL; SEC-16: echo tied to DEBUG flag
_connect_args = {}
if settings.DB_SSL_MODE != "disable":
    import ssl as _ssl
    _ssl_ctx = _ssl.create_default_context()
    _connect_args["ssl"] = _ssl_ctx

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    connect_args=_connect_args,
    pool_size=20,         # Base pool connections (default was 5)
    max_overflow=10,      # Burst capacity above pool_size → max 30 concurrent
    pool_pre_ping=True,   # Verify connections before reuse (prevents stale conn errors)
)
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)
SessionLocal = async_session  # Alias for background task usage

async def get_db():
    async with async_session() as session:
        yield session
