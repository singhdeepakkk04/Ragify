"""
User profile API — view, update, and delete current user's profile.
"""

from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.api import deps
from app.models.user import User

router = APIRouter()


class UserProfile(BaseModel):
    id: int
    email: str
    display_name: Optional[str] = None
    role: str
    is_active: bool

    class Config:
        from_attributes = True


class ProfileUpdate(BaseModel):
    display_name: Optional[str] = Field(None, max_length=100)


@router.get("/me", response_model=UserProfile)
async def get_profile(
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Get current user's profile."""
    return current_user


@router.patch("/me", response_model=UserProfile)
async def update_profile(
    profile_in: ProfileUpdate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Update current user's profile."""
    if profile_in.display_name is not None:
        current_user.display_name = profile_in.display_name
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.delete("/me")
async def delete_account(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Delete current user's account and all associated data."""
    from app.crud.user import delete_user_cascade
    await delete_user_cascade(db, current_user.id)
    return {"detail": "Account and all associated data deleted successfully"}
