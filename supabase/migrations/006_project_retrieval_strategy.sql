-- Per-project retrieval strategy
ALTER TABLE projects 
ADD COLUMN IF NOT EXISTS retrieval_strategy TEXT 
  NOT NULL DEFAULT 'balanced'
  CHECK (retrieval_strategy IN ('fast', 'balanced', 'thorough'));

COMMENT ON COLUMN projects.retrieval_strategy IS 
'fast=no expansion no rerank, balanced=rerank only, thorough=expansion+rerank+web';

-- Onboarding preferences
ALTER TABLE projects
ADD COLUMN IF NOT EXISTS allow_errors BOOLEAN NOT NULL DEFAULT false,
ADD COLUMN IF NOT EXISTS enable_web_search BOOLEAN NOT NULL DEFAULT false;