-- Per-project embedding config
ALTER TABLE projects
ADD COLUMN IF NOT EXISTS embedding_provider TEXT 
  NOT NULL DEFAULT 'openai'
  CHECK (embedding_provider IN ('openai', 'gemini'));

ALTER TABLE projects  
ADD COLUMN IF NOT EXISTS embedding_model TEXT
  NOT NULL DEFAULT 'text-embedding-3-small';

-- document_chunks needs to store which provider was used for that chunk
-- (critical: you cannot mix providers within a project — all chunks must use same space)
ALTER TABLE document_chunks
ADD COLUMN IF NOT EXISTS embedding_provider TEXT;

-- pgvector supports multiple dimensions via separate columns or by storing as 768-padded.
-- Simplest approach: add a second vector column for gemini embeddings (768-dim).
-- Each chunk will have exactly ONE of these populated, based on project's provider.
ALTER TABLE document_chunks
ADD COLUMN IF NOT EXISTS embedding_gemini vector(768);

-- Index for gemini embeddings
CREATE INDEX IF NOT EXISTS idx_chunks_embedding_gemini
  ON document_chunks USING ivfflat (embedding_gemini vector_cosine_ops) WITH (lists = 100);

-- The existing `embedding` column (1536-dim for OpenAI) stays untouched.
-- Comment clarifying the design:
-- embedding        = OpenAI text-embedding-3-small (1536-dim)  
-- embedding_gemini = Gemini Embedding 2 (768-dim, Matryoshka truncated)