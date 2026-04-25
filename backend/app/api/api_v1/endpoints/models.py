"""
Models API — List available AI models for project configuration.
"""

from typing import Any, List
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api import deps
from app.core.model_registry import get_available_models

router = APIRouter()


class ModelResponse(BaseModel):
    id: str
    name: str
    provider: str
    description: str
    context_window: int
    cost_tier: str
    available: bool


@router.get("/", response_model=List[ModelResponse])
async def list_models(
    current_user=Depends(deps.get_current_active_user),
) -> Any:
    """List all supported AI models and their availability."""
    return get_available_models()
