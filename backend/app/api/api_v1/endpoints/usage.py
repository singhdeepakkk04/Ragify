"""
Usage metrics API — aggregated analytics per user.
"""

from typing import Any, List, Optional
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, func, select
from pydantic import BaseModel

from app.api import deps
from app.models.user import User
from app.models.usage_log import UsageLog
from app.models.document import Document
from app.models.project import Project
from app.core.rate_limiter import get_remaining_requests, check_default_rate_limit

router = APIRouter()


class UsageStats(BaseModel):
    total_queries: int
    queries_today: int
    queries_this_week: int
    total_documents: int
    total_projects: int
    avg_latency_ms: float
    rate_limit: dict
    model_breakdown: list
    project_breakdown: list
    recent_queries: list
    daily_usage: list


@router.get("/", response_model=UsageStats)
async def get_usage(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(check_default_rate_limit),
) -> Any:
    """Get comprehensive usage metrics for the current user."""
    user_id = current_user.id
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=7)

    # Total queries
    total_q = await db.execute(
        text("SELECT COUNT(*) FROM usage_logs WHERE user_id = :uid"),
        {"uid": user_id}
    )
    total_queries = total_q.scalar() or 0

    # Queries today
    today_q = await db.execute(
        text("SELECT COUNT(*) FROM usage_logs WHERE user_id = :uid AND created_at >= :start"),
        {"uid": user_id, "start": today_start}
    )
    queries_today = today_q.scalar() or 0

    # Queries this week
    week_q = await db.execute(
        text("SELECT COUNT(*) FROM usage_logs WHERE user_id = :uid AND created_at >= :start"),
        {"uid": user_id, "start": week_start}
    )
    queries_this_week = week_q.scalar() or 0

    # Average latency
    lat_q = await db.execute(
        text("SELECT COALESCE(AVG(latency_ms), 0) FROM usage_logs WHERE user_id = :uid"),
        {"uid": user_id}
    )
    avg_latency_ms = round(float(lat_q.scalar() or 0), 1)

    # Total documents
    doc_q = await db.execute(
        text("""
            SELECT COUNT(*) FROM documents d
            JOIN projects p ON d.project_id = p.id
            WHERE p.owner_id = :uid
        """),
        {"uid": user_id}
    )
    total_documents = doc_q.scalar() or 0

    # Total projects
    proj_q = await db.execute(
        text("SELECT COUNT(*) FROM projects WHERE owner_id = :uid"),
        {"uid": user_id}
    )
    total_projects = proj_q.scalar() or 0

    # Model breakdown
    # Remove ' (cached)' suffix to group base models together
    model_q = await db.execute(
        text("""
            SELECT REPLACE(model_used, ' (cached)', '') as base_model, COUNT(*) as count
            FROM usage_logs WHERE user_id = :uid
            GROUP BY base_model ORDER BY count DESC
        """),
        {"uid": user_id}
    )
    model_breakdown = [{"model": r[0], "count": r[1]} for r in model_q.fetchall()]

    # Project breakdown
    proj_break_q = await db.execute(
        text("""
            SELECT p.name, COUNT(u.id) as count, COALESCE(AVG(u.latency_ms), 0) as avg_latency
            FROM usage_logs u
            JOIN projects p ON u.project_id = p.id
            WHERE u.user_id = :uid
            GROUP BY p.name ORDER BY count DESC LIMIT 10
        """),
        {"uid": user_id}
    )
    project_breakdown = [
        {"project": r[0], "queries": r[1], "avg_latency": round(float(r[2]), 1)}
        for r in proj_break_q.fetchall()
    ]

    # Recent queries (last 20)
    recent_q = await db.execute(
        text("""
            SELECT u.query, u.model_used, u.latency_ms, u.created_at, p.name as project_name
            FROM usage_logs u
            JOIN projects p ON u.project_id = p.id
            WHERE u.user_id = :uid
            ORDER BY u.created_at DESC LIMIT 20
        """),
        {"uid": user_id}
    )
    recent_queries = [
        {
            "query": r[0],
            "model": r[1],
            "latency_ms": r[2],
            "timestamp": r[3].isoformat() if r[3] else "",
            "project": r[4],
        }
        for r in recent_q.fetchall()
    ]

    # Daily usage (last 7 days)
    daily_q = await db.execute(
        text("""
            SELECT DATE(created_at) as day, COUNT(*) as count
            FROM usage_logs WHERE user_id = :uid AND created_at >= :start
            GROUP BY DATE(created_at) ORDER BY day ASC
        """),
        {"uid": user_id, "start": week_start}
    )
    daily_usage = [
        {"date": str(r[0]), "queries": r[1]}
        for r in daily_q.fetchall()
    ]

    # Rate limit status
    rate_limit = await get_remaining_requests(user_id)

    return UsageStats(
        total_queries=total_queries,
        queries_today=queries_today,
        queries_this_week=queries_this_week,
        total_documents=total_documents,
        total_projects=total_projects,
        avg_latency_ms=avg_latency_ms,
        rate_limit=rate_limit,
        model_breakdown=model_breakdown,
        project_breakdown=project_breakdown,
        recent_queries=recent_queries,
        daily_usage=daily_usage,
    )


class ProjectLog(BaseModel):
    id: int
    query: str
    model_used: str
    tokens_used: int
    latency_ms: int
    created_at: str


class ProjectLogsResponse(BaseModel):
    total: int
    logs: list[ProjectLog]


@router.get("/project/{project_id}", response_model=ProjectLogsResponse)
async def get_project_logs(
    project_id: int,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(check_default_rate_limit),
) -> Any:
    """Get usage logs for a specific project."""
    # Verify the user owns the project
    from app.crud import project as crud_project
    project = await crud_project.get_project(db, project_id=project_id, user_id=current_user.id)
    if not project:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Project not found")

    count_q = await db.execute(
        text("SELECT COUNT(*) FROM usage_logs WHERE project_id = :pid AND user_id = :uid"),
        {"pid": project_id, "uid": current_user.id}
    )
    total = count_q.scalar() or 0

    logs_q = await db.execute(
        text("""
            SELECT id, query, model_used, tokens_used, latency_ms, created_at
            FROM usage_logs
            WHERE project_id = :pid AND user_id = :uid
            ORDER BY created_at DESC
            LIMIT :lim OFFSET :off
        """),
        {"pid": project_id, "uid": current_user.id, "lim": limit, "off": offset}
    )
    logs = [
        ProjectLog(
            id=r[0],
            query=r[1],
            model_used=r[2],
            tokens_used=r[3],
            latency_ms=r[4],
            created_at=r[5].isoformat() if r[5] else "",
        )
        for r in logs_q.fetchall()
    ]

    return ProjectLogsResponse(total=total, logs=logs)
