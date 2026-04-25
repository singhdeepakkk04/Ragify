from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class DocumentBase(BaseModel):
    filename: str
    project_id: int


class DocumentCreate(DocumentBase):
    pass


class DocumentUpdate(BaseModel):
    status: Optional[str] = None
    content: Optional[str] = None


class DocumentInDBBase(DocumentBase):
    id: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class Document(DocumentInDBBase):
    pass
