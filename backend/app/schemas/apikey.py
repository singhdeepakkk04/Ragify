from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class APIKeyBase(BaseModel):
    name: Optional[str] = None
    project_id: int

class APIKeyCreate(APIKeyBase):
    pass

class APIKey(APIKeyBase):
    id: int
    prefix: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class APIKeyWithPlaintext(APIKey):
    """Returned exactly once upon creation so the user can copy the full key."""
    plaintext_key: str
