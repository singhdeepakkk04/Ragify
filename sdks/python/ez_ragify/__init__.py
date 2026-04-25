"""
ez-ragify Python SDK — Build RAG pipelines with a single API call.

Usage:
    from ez_ragify import EzRagify

    client = EzRagify(api_key="rag_...")
    response = client.query("What does the doc say?", project_id=1)
    print(response.answer)
"""

from ez_ragify._client import EzRagify, AsyncEzRagify
from ez_ragify._types import (
    Project,
    Document,
    QueryResponse,
    Citation,
    UsageStats,
    ProjectLog,
    ProjectLogs,
    UserProfile,
    Model,
    APIKey,
    Feedback,
)
from ez_ragify._exceptions import (
    EzRagifyError,
    AuthenticationError,
    RateLimitError,
    NotFoundError,
    ValidationError,
)

__version__ = "0.1.0"

__all__ = [
    "EzRagify",
    "AsyncEzRagify",
    "Project",
    "Document",
    "QueryResponse",
    "Citation",
    "UsageStats",
    "ProjectLog",
    "ProjectLogs",
    "UserProfile",
    "Model",
    "APIKey",
    "Feedback",
    "EzRagifyError",
    "AuthenticationError",
    "RateLimitError",
    "NotFoundError",
    "ValidationError",
]
