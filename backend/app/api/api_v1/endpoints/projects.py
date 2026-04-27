from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.crud import project as crud_project
from app.models.user import User
from app.schemas.project import ProjectCreate, Project, ProjectUpdate
from app.core.rate_limiter import check_mutation_rate_limit, check_default_rate_limit

router = APIRouter()


@router.post("", response_model=Project)
async def create_project(
    *,
    db: AsyncSession = Depends(deps.get_db),
    project_in: ProjectCreate,
    current_user: User = Depends(check_mutation_rate_limit),
) -> Any:
    """Create a new project."""
    project = await crud_project.create_project(db, project=project_in, user_id=current_user.id)
    return project


@router.get("/models", response_model=List[dict])
async def list_available_models(
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """List all available LLM models from the registry."""
    from app.core.model_registry import get_available_models
    return get_available_models()


@router.get("", response_model=List[Project])
async def list_projects(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(check_default_rate_limit),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """List all projects for the current user."""
    projects = await crud_project.get_projects(db, user_id=current_user.id, skip=skip, limit=limit)
    return projects


@router.get("/{project_id}", response_model=Project)
async def get_project(
    *,
    db: AsyncSession = Depends(deps.get_db),
    project_id: int,
    current_user: User = Depends(check_default_rate_limit),
) -> Any:
    """Get a specific project."""
    project = await crud_project.get_project(db, project_id=project_id, user_id=current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.delete("/{project_id}", response_model=Project)
async def delete_project(
    *,
    db: AsyncSession = Depends(deps.get_db),
    project_id: int,
    current_user: User = Depends(check_mutation_rate_limit),
) -> Any:
    """Delete a project."""
    project = await crud_project.delete_project(db, project_id=project_id, user_id=current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.patch("/{project_id}", response_model=Project)
async def update_project(
    *,
    db: AsyncSession = Depends(deps.get_db),
    project_id: int,
    project_in: ProjectUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Update a project configuration."""
    project = await crud_project.get_project(db, project_id=project_id, user_id=current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project_in.embedding_provider and project_in.embedding_provider != project.embedding_provider:
        # Check if there are existing documents
        from app.models.document import Document
        from sqlalchemy import select
        result = await db.execute(select(Document.id).where(Document.project_id == project_id).limit(1))
        if result.scalars().first():
            raise HTTPException(status_code=409, detail="Changing embedding provider requires re-ingesting all documents. Delete all documents first, then update the provider.")

    project = await crud_project.update_project(db, project_id=project_id, project_update=project_in, user_id=current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


from app.schemas.apikey import APIKey, APIKeyWithPlaintext
from app.crud.apikey import get_api_keys, create_api_key
from app.schemas.apikey import APIKeyCreate

@router.get("/{project_id}/api-key", response_model=APIKey)
async def get_project_api_key(
    *,
    db: AsyncSession = Depends(deps.get_db),
    project_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Get the API key for a project (owner only). Returns only the prefix."""
    # 1. Verify ownership
    project = await crud_project.get_project(db, project_id=project_id, user_id=current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    # 2. Get key
    keys = await get_api_keys(db, project_id=project_id)
    if not keys:
        # If no key exists yet, we let them fetch null or auto-generate one.
        # But auto-generating here is bad UX because they won't see the plaintext key.
        # So we raise 404, forcing them to hit the regenerate endpoint to get one.
        raise HTTPException(status_code=404, detail="No API Key found. Please generate one.")
        
    return keys[0] # Return the first key prefix for now


@router.post("/{project_id}/api-key/regenerate", response_model=APIKeyWithPlaintext)
async def regenerate_project_api_key(
    *,
    db: AsyncSession = Depends(deps.get_db),
    project_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Regenerate the API key for a project (owner only). Returns the FULL key EXACTLY ONCE."""
    # 1. Verify ownership
    project = await crud_project.get_project(db, project_id=project_id, user_id=current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # 2. Invalidate old keys (delete them for simplicity in this MVP)
    from sqlalchemy import delete
    from app.models.apikey import APIKey as DBAPIKey
    await db.execute(delete(DBAPIKey).where(DBAPIKey.project_id == project_id))
    
    # 3. Create new key
    new_key = await create_api_key(db, APIKeyCreate(project_id=project_id, name="Default Key"))
    await db.commit() # commit the delete
    
    return new_key
