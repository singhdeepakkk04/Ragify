
import os
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile
from app.crud import project as crud_project

from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector
from langchain_core.documents import Document as LC_Document

from app.core.config import settings

# Database connection string for PGVector (Synchronous driver needed for some LangChain Integrations or Async?)
# langchain-postgres supports async, but standard PGVector usage often uses psycopg2.
# We will use the connection string from settings but ensure it uses a supported driver.
# settings.SQLALCHEMY_DATABASE_URI is usually async (postgresql+asyncpg).
# We might need a sync connection string for standard PGVector or use the async methods if available.

# For simplicity in this implementation, we'll use the synchronous `psycopg2` driver for the vector store
# initialization as it's the robust standard for LangChain's PGVector right now.
# We'll construct a sync URL from the async one or settings.

DB_CONNECTION = str(settings.SQLALCHEMY_DATABASE_URI).replace("+asyncpg", "+psycopg2")

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

def get_vector_store(collection_name: str):
    return PGVector(
        embeddings=embeddings,
        collection_name=collection_name,
        connection=DB_CONNECTION,
        use_jsonb=True,
    )

async def process_document(db: AsyncSession, file_path: str, project_id: int, document_id: int):
    """
    Load, split, and embed a document.
    """
    # 1. Load document
    docs = []
    if file_path.endswith(".pdf"):
        loader = PyPDFLoader(file_path)
        docs = loader.load()
    elif file_path.endswith(".docx"):
        loader = Docx2txtLoader(file_path)
        docs = loader.load()
    elif file_path.endswith(".txt"):
        loader = TextLoader(file_path)
        docs = loader.load()
    else:
        # Fallback or error
        return

    # Fetch project settings
    project = await crud_project.get(db, id=project_id)
    if not project:
         print(f"Project {project_id} not found during ingestion")
         return

    # 2. Split text
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=project.chunk_size,
        chunk_overlap=project.chunk_overlap,
        length_function=len,
    )
    splits = text_splitter.split_documents(docs)

    # 3. Add Metadata
    for split in splits:
        split.metadata["project_id"] = project_id
        split.metadata["document_id"] = document_id
        split.metadata["source"] = os.path.basename(file_path)

    # 4. Storage (Vector DB)
    # We use a single collection "ragify_vectors" and filter by project_id in retrieval
    # Or we can use separate collections per project. 
    # Metadata filtering is usually better for resource sharing.
    vector_store = get_vector_store(collection_name="ragify_vectors")
    
    # PGVector.add_documents is typically synchronous in langchain-community < 0.2
    # but langchain-postgres is newer.
    # We will run this in a threadpool if it's sync, or await provided method.
    # 'uadd_documents' or similar is not standard yet in all versions.
    # We'll assume standard sync `add_documents` for now and wrap if needed, 
    # but since this is called from a BackgroundTask, blocking is acceptable-ish 
    # (though ideally we run in run_in_executor).
    
    # Note: langchain_postgres might use async. Let's stick to standard sync for stability now.
    vector_store.add_documents(splits)

    return len(splits)
