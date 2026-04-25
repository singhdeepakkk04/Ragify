"""
Admin API — system-wide stats and user management.
Requires admin role (enforced by get_current_active_admin dependency).
"""

from typing import Any, List
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from pydantic import BaseModel

from app.api import deps
from app.models.user import User
from app.models.project import Project
from app.models.document import Document
from app.models.usage_log import UsageLog
from app.core.rate_limiter import _enforce_rate_limit

router = APIRouter()


class AdminStats(BaseModel):
    total_users: int
    total_projects: int
    total_documents: int
    total_queries: int
    active_users_7d: int


class AdminUser(BaseModel):
    id: int
    email: str
    role: str
    is_active: bool

    class Config:
        from_attributes = True


@router.get("/stats", response_model=AdminStats)
async def admin_stats(
    db: AsyncSession = Depends(deps.get_db),
    _admin: User = Depends(deps.get_current_active_admin),
) -> Any:
    """Get system-wide statistics. Admin only."""
    await _enforce_rate_limit(_admin.id, "admin", 30, 60)
    users_q = await db.execute(select(func.count(User.id)))
    projects_q = await db.execute(select(func.count(Project.id)))
    docs_q = await db.execute(select(func.count(Document.id)))
    queries_q = await db.execute(select(func.count(UsageLog.id)))

    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    active_q = await db.execute(
        select(func.count(func.distinct(UsageLog.user_id))).where(
            UsageLog.created_at >= week_ago
        )
    )

    return AdminStats(
        total_users=users_q.scalar() or 0,
        total_projects=projects_q.scalar() or 0,
        total_documents=docs_q.scalar() or 0,
        total_queries=queries_q.scalar() or 0,
        active_users_7d=active_q.scalar() or 0,
    )


@router.get("/users", response_model=List[AdminUser])
async def admin_list_users(
    db: AsyncSession = Depends(deps.get_db),
    _admin: User = Depends(deps.get_current_active_admin),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """List all users. Admin only."""
    await _enforce_rate_limit(_admin.id, "admin", 30, 60)
    result = await db.execute(
        select(User).order_by(User.created_at.desc()).offset(skip).limit(min(limit, 500))
    )
    return result.scalars().all()


@router.patch("/users/{user_id}/role")
async def admin_update_role(
    user_id: int,
    role: str,
    db: AsyncSession = Depends(deps.get_db),
    admin: User = Depends(deps.get_current_active_admin),
) -> Any:
    """Update a user's role. Admin only."""
    await _enforce_rate_limit(admin.id, "admin", 30, 60)
    if role not in ("user", "admin"):
        raise HTTPException(status_code=400, detail="Role must be 'user' or 'admin'")
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="Cannot change your own role")

    result = await db.execute(select(User).filter(User.id == user_id))
    target = result.scalars().first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    target.role = role
    db.add(target)
    await db.commit()
    return {"detail": f"User {user_id} role updated to {role}"}


@router.patch("/users/{user_id}/status")
async def admin_toggle_user(
    user_id: int,
    is_active: bool,
    db: AsyncSession = Depends(deps.get_db),
    admin: User = Depends(deps.get_current_active_admin),
) -> Any:
    """Activate/deactivate a user. Admin only."""
    await _enforce_rate_limit(admin.id, "admin", 30, 60)
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="Cannot deactivate yourself")

    result = await db.execute(select(User).filter(User.id == user_id))
    target = result.scalars().first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    target.is_active = is_active
    db.add(target)
    await db.commit()
    return {"detail": f"User {user_id} is_active set to {is_active}"}
