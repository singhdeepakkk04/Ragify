from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, Float, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    project_type = Column(String, nullable=False) # ITR, Policy, Banking, BYOR
    
    # Advanced Configuration
    llm_model = Column(String, default="gpt-3.5-turbo")
    embedding_model = Column(String, default="text-embedding-3-small")
    embedding_provider = Column(String, default="openai")
    temperature = Column(Float, default=0.0)
    chunk_size = Column(Integer, default=1000)
    chunk_overlap = Column(Integer, default=200)
    top_k = Column(Integer, default=4)
    deployment_environment = Column(String, default="dev")
    is_public = Column(Boolean, default=False)
    
    retrieval_strategy = Column(String, default="balanced")
    allow_errors = Column(Boolean, default=False)
    enable_web_search = Column(Boolean, default=False)
    
    config = Column(JSON, nullable=True) # For any extra specific settings
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", backref="projects")
