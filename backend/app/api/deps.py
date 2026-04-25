import logging
import time
import threading
from typing import Optional
from fastapi import Depends, HTTPException, status, Header, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
import jwt as pyjwt
import httpx

logger = logging.getLogger(__name__)
security = HTTPBearer()

# ── JWKS cache (SEC-03) ─────────────────────────────────────────────────────
_jwks_cache: dict = {}
_jwks_cache_lock = threading.Lock()
_JWKS_CACHE_TTL = 86400  # 24-hour TTL


def _get_jwks(supabase_url: str) -> dict:
    """Fetch JWKS with 24-hour cache and TLS verification."""
    now = time.time()
    with _jwks_cache_lock:
        cached = _jwks_cache.get("data")
        cached_at = _jwks_cache.get("fetched_at", 0)
        if cached and (now - cached_at) < _JWKS_CACHE_TTL:
            return cached

    jwks_url = f"{supabase_url.rstrip('/')}/auth/v1/.well-known/jwks.json"
    resp = httpx.get(jwks_url, timeout=5.0, verify=True)
    resp.raise_for_status()
    jwks = resp.json()

    with _jwks_cache_lock:
        _jwks_cache["data"] = jwks
        _jwks_cache["fetched_at"] = now
    return jwks


def _decode_supabase_jwt(token: str) -> Optional[dict]:
    """
    Decode a Supabase JWT locally — no network call to Supabase required
    (JWKS is cached for 24 hours).
    Handles both:
      - Legacy HS256 (Shared Secret) — verified with SUPABASE_JWT_SECRET
      - New ECC P-256 (ES256) — verified via Supabase JWKS public endpoint
    Returns (payload, verified) tuple encoded as a dict with a _verified flag.
    """
    secret = getattr(settings, "SUPABASE_JWT_SECRET", "") or ""
    supabase_url = getattr(settings, "SUPABASE_URL", "") or ""

    # SEC-02: Signature verification guarantees token origin.
    # Issuer is validated when SUPABASE_URL is available (defense-in-depth).
    # aud/sub validation kept relaxed: Supabase audience varies by client SDK,
    # and sub is always a UUID that we don't need to verify structurally.
    expected_issuer = f"{supabase_url.rstrip('/')}/auth/v1" if supabase_url else None
    options = {
        "verify_aud": False,
        "verify_iss": bool(expected_issuer),
        "verify_sub": False,
        "verify_exp": True,
    }

    # 1. Try HS256 with local secret (legacy tokens)
    if secret:
        try:
            payload = pyjwt.decode(
                token, secret,
                algorithms=["HS256"],
                options=options,
                **({
                    "issuer": expected_issuer,
                } if expected_issuer else {}),
            )
            payload["_verified"] = True
            return payload
        except pyjwt.ExpiredSignatureError:
            return None
        except pyjwt.InvalidSignatureError:
            pass  # Not HS256 — fall through to ES256
        except Exception as e:
            logger.debug(f"HS256 Decode failed (trying ES256 next): {e}")
            pass

    # 2. Try ES256 via cached JWKS (new ECC P-256 tokens)
    if supabase_url:
        try:
            import json as _json
            jwks = _get_jwks(supabase_url)
            # Find the matching key by kid
            header = pyjwt.get_unverified_header(token)
            kid = header.get("kid")
            key = None
            for k in jwks.get("keys", []):
                if not kid or k.get("kid") == kid:
                    key = pyjwt.algorithms.ECAlgorithm.from_jwk(_json.dumps(k))
                    break
            if key:
                payload = pyjwt.decode(
                    token, key,
                    algorithms=["ES256"],
                    options=options,
                    issuer=expected_issuer,
                )
                payload["_verified"] = True
                return payload
        except pyjwt.ExpiredSignatureError:
            return None
        except Exception as e:
            logger.debug(f"ES256 JWKS verification failed: {e}")

    # SEC-01: No unverified fallback — reject if signature cannot be verified
    logger.warning("JWT verification failed: no valid verification method available")
    return None


async def get_user_from_token(
    db: AsyncSession,
    token: str,
) -> Optional[User]:
    """Validate Supabase JWT locally and return/create the local user."""
    payload = _decode_supabase_jwt(token)
    if not payload:
        return None

    # SEC-13: Only auto-create users from tokens that passed signature verification
    token_verified = payload.pop("_verified", False)

    # Supabase puts email in top-level 'email' field
    email = payload.get("email")
    if not email:
        return None

    result = await db.execute(select(User).filter(User.email == email))
    user = result.scalars().first()

    if user is None:
        if not token_verified:
            logger.warning(f"Refusing to auto-create user from unverified token: {email}")
            return None
        import secrets as _secrets
        user = User(
            email=email,
            hashed_password=_secrets.token_hex(32),  # random — auth is via Supabase
            is_active=True,
            role="user",
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    return user


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    user = await get_user_from_token(db, credentials.credentials)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_active_admin(
    current_user: User = Depends(get_current_active_user),
) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Insufficient privileges")
    return current_user


# --- Dual Auth Support (Bearer token OR API Key) ---
from app.models.apikey import APIKey
from app.models.project import Project


async def get_authenticated_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    security_creds: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
) -> User:
    """
    Authenticate using X-API-Key (priority) OR Bearer Token.
    Returns the User (project owner for API keys).
    """
    # 1. Try API Key
    if x_api_key:
        import hashlib
        key_hash = hashlib.sha256(x_api_key.encode()).hexdigest()
        result = await db.execute(select(APIKey).filter(APIKey.key_hash == key_hash, APIKey.is_active == True))
        db_key = result.scalars().first()
        if db_key:
            result = await db.execute(select(Project).filter(Project.id == db_key.project_id))
            project = result.scalars().first()
            if project:
                result = await db.execute(select(User).filter(User.id == project.owner_id))
                user = result.scalars().first()
                if user and user.is_active:
                    request.state.api_key_project = project
                    return user
        raise HTTPException(status_code=401, detail="Invalid API Key")

    # 2. Try Bearer Token
    if security_creds:
        user = await get_user_from_token(db, security_creds.credentials)
        if user and user.is_active:
            return user

    raise HTTPException(status_code=401, detail="Not authenticated")


async def get_project_by_api_key(
    api_key: str = Header(..., alias="X-API-Key"),
    db: AsyncSession = Depends(get_db),
) -> Project:
    """Authenticate request using X-API-Key header. Returns the associated Project."""
    import hashlib
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    result = await db.execute(select(APIKey).filter(APIKey.key_hash == key_hash, APIKey.is_active == True))
    db_key = result.scalars().first()
    if not db_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive API Key",
        )
    result = await db.execute(select(Project).filter(Project.id == db_key.project_id))
    project = result.scalars().first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project
