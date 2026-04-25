-- ============================================================
-- RAGify — Row Level Security (RLS) Policies
-- Run this in: Supabase Dashboard → SQL Editor → New Query
-- ============================================================

-- ── PROJECTS TABLE ───────────────────────────────────────────

-- Enable RLS
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;

-- Users can only see their own projects
CREATE POLICY "Users can view own projects"
  ON projects FOR SELECT
  USING (auth.uid()::text = owner_id::text);

-- Users can only insert projects for themselves
CREATE POLICY "Users can create own projects"
  ON projects FOR INSERT
  WITH CHECK (auth.uid()::text = owner_id::text);

-- Users can only update their own projects
CREATE POLICY "Users can update own projects"
  ON projects FOR UPDATE
  USING (auth.uid()::text = owner_id::text);

-- Users can only delete their own projects
CREATE POLICY "Users can delete own projects"
  ON projects FOR DELETE
  USING (auth.uid()::text = owner_id::text);


-- ── DOCUMENTS TABLE ──────────────────────────────────────────

-- Enable RLS
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- Users can view documents that belong to their projects
CREATE POLICY "Users can view own documents"
  ON documents FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM projects
      WHERE projects.id = documents.project_id
        AND auth.uid()::text = projects.owner_id::text
    )
  );

-- Users can insert documents into their own projects
CREATE POLICY "Users can upload to own projects"
  ON documents FOR INSERT
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM projects
      WHERE projects.id = documents.project_id
        AND auth.uid()::text = projects.owner_id::text
    )
  );

-- Users can update documents in their own projects
CREATE POLICY "Users can update own documents"
  ON documents FOR UPDATE
  USING (
    EXISTS (
      SELECT 1 FROM projects
      WHERE projects.id = documents.project_id
        AND auth.uid()::text = projects.owner_id::text
    )
  );

-- Users can delete documents from their own projects
CREATE POLICY "Users can delete own documents"
  ON documents FOR DELETE
  USING (
    EXISTS (
      SELECT 1 FROM projects
      WHERE projects.id = documents.project_id
        AND auth.uid()::text = projects.owner_id::text
    )
  );


-- ── BACKEND SERVICE ROLE BYPASS ──────────────────────────────
-- The backend uses the service_role key (SUPABASE_KEY in .env),
-- which automatically bypasses RLS. No extra policy needed.
-- If you're using the anon key in the backend, add this:
--
-- CREATE POLICY "Service role bypass"
--   ON projects FOR ALL
--   USING (auth.role() = 'service_role');


-- ── VERIFY ───────────────────────────────────────────────────
-- After running, verify with:
-- SELECT tablename, rowsecurity FROM pg_tables
-- WHERE tablename IN ('projects', 'documents');
