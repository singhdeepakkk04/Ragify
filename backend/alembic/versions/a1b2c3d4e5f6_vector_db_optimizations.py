"""
Add HNSW index + denormalized user_id & project_id to document_chunks

Revision ID: a1b2c3d4e5f6
Revises: 9b36bf1b9ce3
Create Date: 2026-03-07

Zero-downtime migration in two phases:
  Phase 1 (transactional): Add + backfill user_id / project_id columns
  Phase 2 (non-transactional): CONCURRENTLY build indexes outside any transaction

NOTE: CREATE INDEX CONCURRENTLY requires running OUTSIDE a transaction block.
      We set transaction_per_migration = False on this revision so Alembic
      does NOT wrap the upgrade() function in a BEGIN/COMMIT automatically.
      The column DDL is committed by explicit op.execute("COMMIT") before the indexes.
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '9b36bf1b9ce3'
branch_labels = None
depends_on = None

# CRITICAL: Disable Alembic's automatic transaction wrapping.
# CREATE INDEX CONCURRENTLY MUST run outside any transaction block.
transaction_per_migration = False


def upgrade() -> None:
    conn = op.get_bind()

    # ── Phase 1 (run inside a manual transaction) ─────────────────────────────
    conn.execute(sa.text("BEGIN"))

    # Step 1: Add nullable columns (safe on any table size — no rewrite)
    conn.execute(sa.text("ALTER TABLE document_chunks ADD COLUMN IF NOT EXISTS user_id INTEGER"))
    conn.execute(sa.text("ALTER TABLE document_chunks ADD COLUMN IF NOT EXISTS project_id INTEGER"))

    # Step 2: Backfill from JOIN chain in a single efficient UPDATE
    conn.execute(sa.text("""
        UPDATE document_chunks dc
        SET
            project_id = d.project_id,
            user_id    = p.owner_id
        FROM documents d
        JOIN projects p ON p.id = d.project_id
        WHERE dc.document_id = d.id
          AND (dc.user_id IS NULL OR dc.project_id IS NULL)
    """))

    # Step 3: Enforce NOT NULL after backfill
    conn.execute(sa.text("ALTER TABLE document_chunks ALTER COLUMN user_id SET NOT NULL"))
    conn.execute(sa.text("ALTER TABLE document_chunks ALTER COLUMN project_id SET NOT NULL"))

    conn.execute(sa.text("COMMIT"))

    # ── Phase 2 (CONCURRENTLY — must run OUTSIDE a transaction block) ─────────

    # Step 4: Composite B-tree index — replaces 2-hop JOIN for user/project filtering
    conn.execute(sa.text("""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_dc_user_project
        ON document_chunks (user_id, project_id)
    """))

    # Step 5: HNSW ANN index — enables sub-linear nearest-neighbor vector search
    # m=16 (connections per node), ef_construction=64 (build quality vs time)
    # This may take several minutes on large datasets (visible in pg_stat_progress_create_index)
    conn.execute(sa.text("""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_dc_embedding_hnsw
        ON document_chunks
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64)
    """))


def downgrade() -> None:
    conn = op.get_bind()

    conn.execute(sa.text("DROP INDEX CONCURRENTLY IF EXISTS ix_dc_embedding_hnsw"))
    conn.execute(sa.text("DROP INDEX CONCURRENTLY IF EXISTS ix_dc_user_project"))

    conn.execute(sa.text("BEGIN"))
    conn.execute(sa.text("ALTER TABLE document_chunks ALTER COLUMN project_id DROP NOT NULL"))
    conn.execute(sa.text("ALTER TABLE document_chunks ALTER COLUMN user_id DROP NOT NULL"))
    conn.execute(sa.text("ALTER TABLE document_chunks DROP COLUMN IF EXISTS project_id"))
    conn.execute(sa.text("ALTER TABLE document_chunks DROP COLUMN IF EXISTS user_id"))
    conn.execute(sa.text("COMMIT"))
