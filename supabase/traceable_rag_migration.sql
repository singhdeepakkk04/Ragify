-- Traceable RAG Upgrade Migration
-- Adds page_number, metadata, and search_vector to document_chunks
-- Run in Supabase SQL Editor

-- 1. Add new columns
ALTER TABLE document_chunks ADD COLUMN IF NOT EXISTS page_number INTEGER;
ALTER TABLE document_chunks ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}';
ALTER TABLE document_chunks ADD COLUMN IF NOT EXISTS search_vector tsvector;

-- 2. Create GIN index for fast full-text search (BM25)
CREATE INDEX IF NOT EXISTS idx_chunks_search_vector ON document_chunks USING GIN(search_vector);

-- 3. Auto-populate search_vector on INSERT/UPDATE via trigger
CREATE OR REPLACE FUNCTION update_search_vector() RETURNS trigger AS $$
BEGIN
    NEW.search_vector := to_tsvector('english', COALESCE(NEW.content, ''));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_update_search_vector ON document_chunks;
CREATE TRIGGER trg_update_search_vector
    BEFORE INSERT OR UPDATE OF content ON document_chunks
    FOR EACH ROW
    EXECUTE FUNCTION update_search_vector();

-- 4. Add ON DELETE CASCADE to document_chunks (if not already set)
-- This ensures deleting a document automatically removes its chunks
ALTER TABLE document_chunks DROP CONSTRAINT IF EXISTS document_chunks_document_id_fkey;
ALTER TABLE document_chunks 
    ADD CONSTRAINT document_chunks_document_id_fkey 
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE;

-- Done! Now re-upload documents to populate the new columns.
