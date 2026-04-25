from typing import List, Optional
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.document import Document, DocumentStatus
from app.schemas.document import DocumentCreate, DocumentUpdate


async def create(db: AsyncSession, obj_in: DocumentCreate) -> Document:
    db_obj = Document(
        filename=obj_in.filename,
        project_id=obj_in.project_id,
        status=DocumentStatus.PENDING,
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


from app.models.project import Project

async def get_multi_by_project(db: AsyncSession, project_id: int, owner_id: int) -> List[Document]:
    result = await db.execute(
        select(Document)
        .join(Project, Document.project_id == Project.id)
        .filter(Document.project_id == project_id, Project.owner_id == owner_id)
        .order_by(Document.created_at.desc())
    )
    return result.scalars().all()


async def get(db: AsyncSession, id: int, owner_id: int) -> Optional[Document]:
    result = await db.execute(
        select(Document)
        .join(Project, Document.project_id == Project.id)
        .filter(Document.id == id, Project.owner_id == owner_id)
    )
    return result.scalars().first()


async def update(db: AsyncSession, db_obj: Document, obj_in) -> Document:
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        if hasattr(db_obj, field):
            setattr(db_obj, field, value)

    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def delete(db: AsyncSession, id: int, owner_id: int) -> Optional[Document]:
    obj = await get(db, id, owner_id)
    if obj:
        # Manually delete chunks first (no CASCADE in model/DB)
        from app.models.document import DocumentChunk
        from sqlalchemy import delete as sql_delete
        
        await db.execute(sql_delete(DocumentChunk).where(DocumentChunk.document_id == id))
        
        await db.delete(obj)
        await db.commit()
    return obj
