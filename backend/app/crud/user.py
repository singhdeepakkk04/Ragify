from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash

async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalars().first()

async def create_user(db: AsyncSession, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def delete_user_cascade(db: AsyncSession, user_id: int) -> None:
    """Delete a user and all associated data (projects, documents, chunks, keys, logs)."""
    from app.models.usage_log import UsageLog
    from app.models.apikey import APIKey
    from app.models.document import Document
    from app.models.project import Project
    from sqlalchemy import text

    # Get all project IDs owned by this user
    result = await db.execute(select(Project.id).filter(Project.owner_id == user_id))
    project_ids = [r[0] for r in result.fetchall()]

    if project_ids:
        # Delete chunks for all user's projects
        await db.execute(
            text("DELETE FROM document_chunks WHERE project_id = ANY(:pids)"),
            {"pids": project_ids}
        )
        # Delete documents for all user's projects
        await db.execute(delete(Document).where(Document.project_id.in_(project_ids)))
        # Delete API keys for all user's projects
        await db.execute(delete(APIKey).where(APIKey.project_id.in_(project_ids)))

    # Delete usage logs
    await db.execute(delete(UsageLog).where(UsageLog.user_id == user_id))
    # Delete projects
    await db.execute(delete(Project).where(Project.owner_id == user_id))
    # Delete the user
    await db.execute(delete(User).where(User.id == user_id))

    await db.commit()
