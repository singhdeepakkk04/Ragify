from typing import Optional, Any, Dict
from pydantic import BaseModel
from datetime import datetime

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    project_type: str # ITR, Policy, Banking, BYOR
    
    # Advanced Config
    llm_model: Optional[str] = "gpt-3.5-turbo"
    embedding_model: Optional[str] = "text-embedding-3-small"
    temperature: Optional[float] = 0.0
    chunk_size: Optional[int] = 1000
    chunk_overlap: Optional[int] = 200
    top_k: Optional[int] = 4
    deployment_environment: Optional[str] = "dev"
    is_public: Optional[bool] = False
    
    config: Optional[Dict[str, Any]] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    project_type: Optional[str] = None
    llm_model: Optional[str] = None
    embedding_model: Optional[str] = None
    temperature: Optional[float] = None
    chunk_size: Optional[int] = None
    chunk_overlap: Optional[int] = None
    top_k: Optional[int] = None
    deployment_environment: Optional[str] = None
    is_public: Optional[bool] = None
    config: Optional[Dict[str, Any]] = None

class ProjectInDBBase(ProjectBase):
    id: int
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class Project(ProjectInDBBase):
    pass
