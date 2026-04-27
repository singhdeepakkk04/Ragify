from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, mapped_column
from sqlalchemy.dialects.postgresql import TSVECTOR
from pgvector.sqlalchemy import Vector
from app.db.base import Base
import enum


class DocumentStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    filename = Column(String, nullable=False)
    content = Column(Text, nullable=True)
    status = Column(String, default=DocumentStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"))

    # Denormalized for fast filtering: avoids JOIN documents→projects on every query.
    # These are populated at indexing time and never change.
    user_id    = Column(Integer, nullable=False, index=True)
    project_id = Column(Integer, nullable=False, index=True)

    content = Column(Text, nullable=False)
    embedding = mapped_column(Vector(1536))  # OpenAI text-embedding-3-small
    embedding_gemini = mapped_column(Vector(768))  # Gemini 2 embedding
    embedding_provider = Column(String, default="openai")
    chunk_index = Column(Integer)
    page_number = Column(Integer, nullable=True)
    chunk_metadata = Column("metadata", JSON, default={})
    search_vector = Column(TSVECTOR)

    document = relationship("Document", back_populates="chunks")
