import logging
import time
from typing import List, Dict
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from app.db.session import async_session
from app.models.document import DocumentStatus, Document, DocumentChunk
from app.models.project import Project
from app.core.config import settings
from app.core.guardrails import sanitize_document_content
from app.services.embedding_service import get_embedding_service, EmbeddingProvider

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def index_document(
    document_id: int,
    pages: List[Dict],
    project_id: int,
    filename: str,
    user_id: int = None,
):
    """
    Background task: page-aware chunk → embed → store with metadata → update status.
    """
    t_start = time.time()
    total_chars = sum(len(p["text"]) for p in pages)
    logger.info(
        f"[Indexing] ▶ Starting document {document_id} "
        f"({len(pages)} pages, {total_chars} chars)"
    )

    async with async_session() as db:
        try:
            # 0. Get the project to determine embedding provider
            project_stmt = await db.execute(select(Project).where(Project.id == project_id))
            project = project_stmt.scalars().first()
            if not project:
                raise ValueError(f"Project {project_id} not found")
            
            provider = project.embedding_provider or "openai"
            
            # SAFETY CHECK: verify all existing chunks use the same provider
            existing_chunk_stmt = await db.execute(
                select(DocumentChunk.embedding_provider).where(DocumentChunk.project_id == project_id).limit(1)
            )
            existing_provider = existing_chunk_stmt.scalars().first()
            if existing_provider and existing_provider != provider:
                raise ValueError(
                    f"Cannot mix embedding providers within a project. "
                    f"This project uses {existing_provider}. "
                    f"Re-ingest all documents after changing the provider."
                )

            # 1. Mark as PROCESSING
            await _set_status(db, document_id, DocumentStatus.PROCESSING)

            # 2. Split each page into chunks
            t1 = time.time()
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000, chunk_overlap=200
            )

            all_chunks: list[dict] = []  
            global_idx = 0
            for page_data in pages:
                page_num = page_data["page"]
                page_text = page_data["text"]
                page_chunks = splitter.split_text(page_text)

                for chunk_text in page_chunks:
                    safe_text = sanitize_document_content(chunk_text)
                    all_chunks.append(
                        {
                            "text": safe_text,
                            "page": page_num,
                            "chunk_index": global_idx,
                        }
                    )
                    global_idx += 1

            logger.info(
                f"[Indexing] Split into {len(all_chunks)} chunks "
                f"across {len(pages)} pages in {time.time()-t1:.2f}s"
            )

            if not all_chunks:
                logger.warning("[Indexing] No chunks extracted — marking FAILED")
                await _set_status(db, document_id, DocumentStatus.FAILED)
                return

            # 3. Generate embeddings
            t2 = time.time()
            texts = [c["text"] for c in all_chunks]
            
            logger.info(f"[Indexing] Calling {provider} for {len(texts)} embeddings...")
            svc = get_embedding_service(provider)
            # Batch embedding
            embeddings = []
            batch_size = 100
            for i in range(0, len(texts), batch_size):
                batch = texts[i : i + batch_size]
                t_batch = time.time()
                logger.info(f"[Indexing] Embedding batch {i // batch_size + 1} ({len(batch)} chunks)...")
                batch_embeddings = await svc.embed_documents_batch(batch)
                logger.info(f"[Indexing] Embedding batch done in {time.time()-t_batch:.2f}s")
                embeddings.extend(batch_embeddings)
            
            logger.info(f"[Indexing] All embeddings done in {time.time()-t2:.2f}s")

            # 4. Store chunks with metadata
            t3 = time.time()
            for chunk_data, vector in zip(all_chunks, embeddings):
                chunk = DocumentChunk(
                    document_id=document_id,
                    user_id=user_id,
                    project_id=project_id,
                    content=chunk_data["text"],
                    chunk_index=chunk_data["chunk_index"],
                    page_number=chunk_data["page"],
                    chunk_metadata={
                        "filename": filename,
                        "page": chunk_data["page"],
                        "project_id": project_id,
                    },
                )
                if provider == EmbeddingProvider.GEMINI:
                    chunk.embedding_gemini = vector
                    chunk.embedding_provider = "gemini"
                else:
                    chunk.embedding = vector         
                    chunk.embedding_provider = "openai"

                db.add(chunk)

            await db.commit()
            logger.info(
                f"[Indexing] {len(all_chunks)} chunks saved to DB "
                f"in {time.time()-t3:.2f}s"
            )

            # 5. Populate search_vector
            t4 = time.time()
            await db.execute(
                text(
                    """
                    UPDATE document_chunks
                    SET search_vector = to_tsvector('english', content)
                    WHERE project_id = :project_id
                      AND document_id = :doc_id
                      AND search_vector IS NULL
                    """
                ),
                {"project_id": project_id, "doc_id": document_id},
            )
            await db.commit()
            logger.info(
                f"[Indexing] search_vector populated in {time.time()-t4:.2f}s"
            )

            # 6. Mark as COMPLETED
            await _set_status(db, document_id, DocumentStatus.COMPLETED)
            logger.info(
                f"[Indexing] ✅ Document {document_id} COMPLETED "
                f"in {time.time()-t_start:.2f}s total"
            )

        except Exception as e:
            logger.error(
                f"[Indexing] ❌ Document {document_id} FAILED "
                f"after {time.time()-t_start:.2f}s: {e}",
                exc_info=True,
            )
            try:
                await db.rollback()
                await _set_status(db, document_id, DocumentStatus.FAILED)
            except Exception as inner:
                logger.error(f"[Indexing] Could not set FAILED status: {inner}")


async def _set_status(db: AsyncSession, document_id: int, status: DocumentStatus):
    result = await db.execute(
        select(Document).filter(Document.id == document_id)
    )
    doc = result.scalars().first()
    if doc:
        doc.status = status
        db.add(doc)
        await db.commit()
