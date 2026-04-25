from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate

async def get_projects(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100) -> List[Project]:
    result = await db.execute(select(Project).filter(Project.owner_id == user_id).order_by(Project.created_at.desc()).offset(skip).limit(limit))
    return result.scalars().all()

async def create_project(db: AsyncSession, project: ProjectCreate, user_id: int) -> Project:
    db_project = Project(**project.model_dump(), owner_id=user_id)
    db.add(db_project)
    await db.commit()
    await db.refresh(db_project)

    # Auto-generate API Key
    from app.crud.apikey import create_api_key
    from app.schemas.apikey import APIKeyCreate
    
    await create_api_key(db, APIKeyCreate(project_id=db_project.id, name="Default Key"))
    
    return db_project

async def get_project(db: AsyncSession, project_id: int, user_id: int) -> Optional[Project]:
    result = await db.execute(select(Project).filter(Project.id == project_id, Project.owner_id == user_id))
    return result.scalars().first()

async def delete_project(db: AsyncSession, project_id: int, user_id: int) -> Optional[Project]:
    result = await db.execute(select(Project).filter(Project.id == project_id, Project.owner_id == user_id))
    project = result.scalars().first()
    
    if project:
        from sqlalchemy import delete
        from app.models.usage_log import UsageLog
        from app.models.apikey import APIKey
        from app.models.document import Document
        
        # Manually cascade delete dependent records to prevent Foreign Key errors
        await db.execute(delete(UsageLog).where(UsageLog.project_id == project_id))
        await db.execute(delete(APIKey).where(APIKey.project_id == project_id))
        await db.execute(delete(Document).where(Document.project_id == project_id))
        
        await db.delete(project)
        await db.commit()
    
    return project

async def update_project(db: AsyncSession, project_id: int, project_update: ProjectUpdate, user_id: int) -> Optional[Project]:
    project = await get_project(db, project_id=project_id, user_id=user_id)
    if not project:
        return None
        
    update_data = project_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(project, key, value)
        
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


async def get(db: AsyncSession, id: int) -> Optional[Project]:
    """Get project by id (no user filter — for internal pipeline use after auth check)."""
    result = await db.execute(select(Project).filter(Project.id == id))
    return result.scalars().first()

