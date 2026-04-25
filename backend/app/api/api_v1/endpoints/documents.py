from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Any
from app.api import deps
from app.crud import document as crud_document
from app.crud import project as crud_project
from app.schemas import document as doc_schemas
from app.core.rag import indexing
import pypdf
import io
import os
import json
from docx import Document as DocxDocument
from app.core.query_cache import query_cache
from app.core.rate_limiter import check_upload_rate_limit, check_default_rate_limit

router = APIRouter()

# ── SEC-07: Magic byte signatures for file type validation ──────────────────
_PDF_MAGIC = b"%PDF"
_DOCX_MAGIC = b"PK\x03\x04"  # DOCX is a ZIP-based format


def _validate_file_magic(file_bytes: bytes, extension: str) -> bool:
    """Validate file content matches expected type via magic bytes."""
    if extension == ".pdf":
        return file_bytes[:4] == _PDF_MAGIC
    elif extension == ".docx":
        return file_bytes[:4] == _DOCX_MAGIC
    elif extension in (".txt", ".md"):
        # Text files: ensure valid UTF-8
        try:
            file_bytes[:2048].decode("utf-8")
            return True
        except UnicodeDecodeError:
            return False
    return False


def _sanitize_filename(filename: str) -> str:
    """SEC-08: Strip path components and dangerous characters from filename."""
    safe = os.path.basename(filename or "unknown_file")
    safe = "".join(c for c in safe if c.isprintable() and c not in '<>"\'\\/')
    return safe[:255] if safe else "unknown_file"


@router.post("/upload", response_model=doc_schemas.Document)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    project_id: int = Form(...),
    db: AsyncSession = Depends(deps.get_db),
    current_user=Depends(check_upload_rate_limit),
) -> Any:
    """
    Upload a document, parse it page-by-page, and start background indexing.
    Verifies the user owns the target project first.
    """
    # 1. Verify Project Ownership
    project = await crud_project.get(db, id=project_id)
    if not project or project.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Project not found")

    # 2. Enforce File Size Limit (HIGH-1)
    MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB limit
    # file.size can be None for chunked uploads — always check actual bytes
    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413, 
            detail=f"File too large. Maximum size is 20MB, but received {len(file_bytes) / (1024*1024):.1f}MB."
        )

    pages: list[dict] = []

    # SEC-08: Sanitize filename from client
    safe_filename = _sanitize_filename(file.filename)

    # Determine extension from the sanitized filename
    _, ext = os.path.splitext(safe_filename)
    ext = ext.lower()

    # SEC-07: Validate file content matches claimed type via magic bytes
    if ext in (".pdf", ".docx", ".txt", ".md"):
        if not _validate_file_magic(file_bytes, ext):
            raise HTTPException(
                status_code=400,
                detail=f"File content does not match the {ext} format. The file may be corrupted or mislabeled.",
            )
    else:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Use PDF, DOCX, TXT, or MD.",
        )

    if ext == ".pdf":
        try:
            pdf = pypdf.PdfReader(io.BytesIO(file_bytes))
            for i, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                if text.strip():
                    pages.append({"page": i + 1, "text": text})
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"PDF parsing error: {e}", exc_info=True)
            raise HTTPException(status_code=400, detail="Invalid PDF file. The file may be corrupt or encrypted.")

    elif ext == ".docx":
        try:
            doc = DocxDocument(io.BytesIO(file_bytes))
            full_text = "\n".join(para.text for para in doc.paragraphs)
            if full_text.strip():
                pages.append({"page": 1, "text": full_text})
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"DOCX parsing error: {e}", exc_info=True)
            raise HTTPException(status_code=400, detail="Invalid DOCX file. The file may be corrupt.")

    elif ext in (".txt", ".md"):
        content = file_bytes.decode("utf-8")
        if content.strip():
            pages.append({"page": 1, "text": content})

    if not pages:
        raise HTTPException(
            status_code=400, detail="Empty file or no text could be extracted."
        )

    # Create Document record
    doc_in = doc_schemas.DocumentCreate(
        filename=safe_filename,
        project_id=project_id,
    )
    doc = await crud_document.create(db, doc_in)

    # Trigger background indexing with page-structured data
    background_tasks.add_task(
        indexing.index_document, doc.id, pages, project_id, safe_filename,
        current_user.id  # user_id for direct tenant-isolated chunk storage
    )

    # Invalidate cache for this project (new document = new answers)
    query_cache.invalidate_project(project_id)

    return doc


@router.get("", response_model=List[doc_schemas.Document])
async def get_documents(
    project_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user=Depends(check_default_rate_limit),
) -> Any:
    """Get all documents for a project, verifying the user owns the project."""
    docs = await crud_document.get_multi_by_project(db, project_id=project_id, owner_id=current_user.id)
    return docs


@router.delete("/{document_id}", response_model=doc_schemas.Document)
async def delete_document(
    document_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user=Depends(check_default_rate_limit),
) -> Any:
    """Delete a document and its chunks, verifying the user owns the project."""
    doc = await crud_document.delete(db, document_id, owner_id=current_user.id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Invalidate cache for the project this doc belonged to
    query_cache.invalidate_project(doc.project_id)
    
    return doc
