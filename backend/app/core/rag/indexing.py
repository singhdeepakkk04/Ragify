import logging
import time
from typing import List, Dict
from langchain.text_splitter import RecursiveCharacterTextSplitter
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from app.db.session import async_session
from app.models.document import DocumentStatus, Document, DocumentChunk
from app.core.config import settings
from app.core.guardrails import sanitize_document_content

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_openai_client = None


def get_openai_client() -> AsyncOpenAI:
    global _openai_client
    if _openai_client is None:
        _openai_client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            timeout=30.0,
            max_retries=2,
        )
    return _openai_client


async def embed_texts(texts: list[str]) -> list[list[float]]:
    """Call OpenAI embeddings API in batches of 100."""
    client = get_openai_client()
    embeddings = []
    batch_size = 100
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        t0 = time.time()
        logger.info(
            f"[Indexing] Embedding batch {i // batch_size + 1} ({len(batch)} chunks)..."
        )
        response = await client.embeddings.create(
            input=batch,
            model="text-embedding-3-small",
        )
        logger.info(f"[Indexing] Embedding batch done in {time.time()-t0:.2f}s")
        embeddings.extend([item.embedding for item in response.data])
    return embeddings


async def index_document(
    document_id: int,
    pages: List[Dict],
    project_id: int,
    filename: str,
    user_id: int = None,
):
    """
    Background task: page-aware chunk → embed → store with metadata → update status.
    
    Args:
        document_id: DB ID of the document
        pages: List of {"page": int, "text": str} — one per PDF page
        project_id: Owner project ID
        filename: Original filename for metadata
        user_id: Owning user ID — stored directly on each chunk for fast tenant-isolated search
    """
    t_start = time.time()
    total_chars = sum(len(p["text"]) for p in pages)
    logger.info(
        f"[Indexing] ▶ Starting document {document_id} "
        f"({len(pages)} pages, {total_chars} chars)"
    )

    async with async_session() as db:
        try:
            # 1. Mark as PROCESSING
            await _set_status(db, document_id, DocumentStatus.PROCESSING)

            # 2. Split each page into chunks (preserving page_number)
            t1 = time.time()
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000, chunk_overlap=200
            )

            all_chunks: list[dict] = []  # {text, page, chunk_index}
            global_idx = 0
            for page_data in pages:
                page_num = page_data["page"]
                page_text = page_data["text"]
                page_chunks = splitter.split_text(page_text)

                for chunk_text in page_chunks:
                    # Neutralize any prompt injection payloads embedded in the document
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
            logger.info(f"[Indexing] Calling OpenAI for {len(texts)} embeddings...")
            embeddings = await embed_texts(texts)
            logger.info(f"[Indexing] All embeddings done in {time.time()-t2:.2f}s")

            # 4. Store chunks with metadata
            t3 = time.time()
            for chunk_data, embedding in zip(all_chunks, embeddings):
                chunk = DocumentChunk(
                    document_id=document_id,
                    # Denormalized tenant/project keys for direct indexed lookup:
                    user_id=user_id,
                    project_id=project_id,
                    content=chunk_data["text"],
                    embedding=embedding,
                    chunk_index=chunk_data["chunk_index"],
                    page_number=chunk_data["page"],
                    chunk_metadata={
                        "filename": filename,
                        "page": chunk_data["page"],
                        "project_id": project_id,
                    },
                )
                db.add(chunk)

            await db.commit()
            logger.info(
                f"[Indexing] {len(all_chunks)} chunks saved to DB "
                f"in {time.time()-t3:.2f}s"
            )

            # 5. Populate search_vector for BM25 via raw SQL
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
