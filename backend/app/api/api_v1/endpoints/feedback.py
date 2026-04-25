from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.core.rate_limiter import check_default_rate_limit
from app.crud import project as crud_project
from app.crud.feedback import create_feedback, get_feedback_by_request
from app.schemas.feedback import FeedbackCreate, FeedbackResponse
from app.models.user import User

router = APIRouter()


@router.post("", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    payload: FeedbackCreate,
    request: Request,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(check_default_rate_limit),
):
    """Record like/dislike feedback for a specific response/request."""
    # If the request was authenticated via API key, enforce project match
    if hasattr(request.state, "api_key_project") and request.state.api_key_project:
        if request.state.api_key_project.id != payload.project_id:
            raise HTTPException(status_code=403, detail="API Key is not authorized for this project.")

    # Verify project ownership
    project = await crud_project.get_project(db, project_id=payload.project_id, user_id=current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Optional idempotency: if feedback already exists for this request/user, reject
    existing = await get_feedback_by_request(db, current_user.id, payload.request_id)
    if existing:
        raise HTTPException(status_code=409, detail="Feedback already recorded for this request")

    feedback = await create_feedback(db, current_user.id, payload)
    return FeedbackResponse.model_validate(feedback)
