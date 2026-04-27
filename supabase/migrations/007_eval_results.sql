-- 007_eval_results.sql
-- RAGAS evaluation scores per query trace.
--
-- Note: This repo's existing Supabase SQL uses integer project IDs (see supabase/usage_log_migration.sql),
-- so project_id is INTEGER here to match the current backend models.

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS eval_results (
    id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id          INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    trace_id            TEXT NOT NULL,
    query_text          TEXT,
    faithfulness        FLOAT CHECK (faithfulness BETWEEN 0 AND 1),
    answer_relevancy    FLOAT CHECK (answer_relevancy BETWEEN 0 AND 1),
    context_precision   FLOAT CHECK (context_precision BETWEEN 0 AND 1),
    query_tier          TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_eval_project_time ON eval_results (project_id, created_at DESC);
