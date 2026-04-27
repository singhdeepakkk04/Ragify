-- 008_usage_analytics.sql
-- Token-level usage analytics for RAG queries.
--
-- Note: This repo's backend uses integer project IDs, so project_id is INTEGER.
-- user_id is UUID to support Supabase auth.users if available; backend can also insert NULL.

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS query_usage (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id           INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    user_id              UUID REFERENCES auth.users(id),
    trace_id             TEXT,
    query_tier           TEXT,

    -- Token counts
    embedding_tokens     INTEGER NOT NULL DEFAULT 0,
    retrieval_chunks     INTEGER NOT NULL DEFAULT 0,
    context_tokens       INTEGER NOT NULL DEFAULT 0,
    completion_tokens    INTEGER NOT NULL DEFAULT 0,
    total_tokens         INTEGER GENERATED ALWAYS AS
                        (embedding_tokens + context_tokens + completion_tokens) STORED,

    -- Web search
    web_search_used      BOOLEAN NOT NULL DEFAULT false,
    web_results_count    INTEGER NOT NULL DEFAULT 0,

    -- Latency
    query_plan_ms        INTEGER,
    retrieval_ms         INTEGER,
    generation_ms        INTEGER,
    total_ms             INTEGER,

    created_at           TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_usage_project_time ON query_usage (project_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_usage_user_time    ON query_usage (user_id, created_at DESC);

-- Dashboard view: daily aggregates per project
CREATE OR REPLACE VIEW project_usage_daily AS
SELECT
    project_id,
    DATE(created_at) AS day,
    COUNT(*)                                   AS total_queries,
    SUM(total_tokens)                          AS total_tokens,
    SUM(completion_tokens)                     AS total_completion_tokens,
    SUM(context_tokens)                        AS total_context_tokens,
    AVG(total_ms)                              AS avg_latency_ms,
    COUNT(*) FILTER (WHERE web_search_used)    AS web_search_queries,
    AVG(total_ms) FILTER (WHERE query_tier = 'fast')     AS avg_fast_ms,
    AVG(total_ms) FILTER (WHERE query_tier = 'balanced') AS avg_balanced_ms,
    AVG(total_ms) FILTER (WHERE query_tier = 'thorough') AS avg_thorough_ms
FROM query_usage
GROUP BY project_id, DATE(created_at);
