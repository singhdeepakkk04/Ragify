import secrets
import hashlib
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.apikey import APIKey
from app.schemas.apikey import APIKeyCreate

async def get_api_keys(db: AsyncSession, project_id: int) -> List[APIKey]:
    result = await db.execute(select(APIKey).filter(APIKey.project_id == project_id))
    return result.scalars().all()

async def create_api_key(db: AsyncSession, api_key: APIKeyCreate) -> APIKey:
    # Generate a secure random key
    raw_key = f"rag_{secrets.token_urlsafe(32)}"
    
    # Generate hash and prefix
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    prefix = raw_key[:12] # e.g. "rag_abcdef..."
    
    db_obj = APIKey(
        project_id=api_key.project_id,
        name=api_key.name,
        key_hash=key_hash,
        prefix=prefix
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    
    # Attach the raw key temporarily so the endpoint can return it exactly once
    setattr(db_obj, "plaintext_key", raw_key)
    return db_obj
