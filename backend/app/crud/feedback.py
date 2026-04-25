from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.models.feedback import Feedback
from app.schemas.feedback import FeedbackCreate


async def create_feedback(db: AsyncSession, user_id: int, payload: FeedbackCreate) -> Feedback:
    feedback = Feedback(
        user_id=user_id,
        project_id=payload.project_id,
        request_id=payload.request_id,
        rating=payload.rating,
        comment=payload.comment,
    )
    db.add(feedback)
    await db.commit()
    await db.refresh(feedback)
    return feedback


async def get_feedback_by_request(db: AsyncSession, user_id: int, request_id: str) -> Optional[Feedback]:
    stmt = select(Feedback).where(Feedback.user_id == user_id, Feedback.request_id == request_id)
    res = await db.execute(stmt)
    return res.scalars().first()
