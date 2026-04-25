#!/usr/bin/env python3
"""
migrate_supabase_to_docker.py
Migrates all data from Supabase to local Docker PostgreSQL.
Run from the project root: python migrate_supabase_to_docker.py
"""

import asyncio
import asyncpg
import json
import socket
from datetime import datetime

# ─── Connection strings ────────────────────────────────────────────────────────
SUPABASE_DSN = (
    "postgresql://postgres.hmdscbbetnjohvmfycaw:Myminnu042911"
    "@aws-1-ap-south-1.pooler.supabase.com:5432/postgres"
)
DOCKER_DSN = (
    "postgresql://ragify:ragify_password@localhost:5432/ragify_db"
)

# Tables in FK-safe order (parent before child)
TABLES = ["users", "projects", "api_keys", "documents", "document_chunks"]


def check_port(host: str, port: int, label: str):
    """Quick preflight — raise with a friendly message if port is closed."""
    try:
        with socket.create_connection((host, port), timeout=5):
            pass
    except OSError:
        print(f"\n❌  Cannot reach {label} at {host}:{port}")
        if label == "Docker Postgres":
            print("   → Make sure Docker Desktop is running and containers are up:")
            print("     docker-compose up -d")
        elif label == "Supabase":
            print("   → Resume your Supabase project at https://supabase.com/dashboard")
        raise SystemExit(1)


def serialize(val):
    """Make any value JSON / asyncpg friendly for INSERT."""
    if isinstance(val, dict):
        return json.dumps(val)
    if isinstance(val, datetime):
        return val
    return val


async def get_columns(conn, table: str) -> list[str]:
    rows = await conn.fetch(
        """
        SELECT column_name FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = $1
        ORDER BY ordinal_position
        """,
        table,
    )
    return [r["column_name"] for r in rows]


async def migrate_table(src_conn, dst_conn, table: str):
    print(f"\n📦  Migrating table: {table}")

    # Fetch columns from Docker (the target schema is authoritative)
    cols = await get_columns(dst_conn, table)
    col_list = ", ".join(f'"{c}"' for c in cols)
    placeholders = ", ".join(f"${i+1}" for i in range(len(cols)))

    # Pull all rows from Supabase
    rows = await src_conn.fetch(f'SELECT {col_list} FROM public."{table}"')
    print(f"   Found {len(rows)} rows in Supabase")

    if not rows:
        print("   ⏭️  Nothing to migrate.")
        return

    # Disable FK checks during load, then re-enable
    await dst_conn.execute(f'ALTER TABLE public."{table}" DISABLE TRIGGER ALL')
    try:
        insert_sql = (
            f'INSERT INTO public."{table}" ({col_list}) VALUES ({placeholders}) '
            f'ON CONFLICT DO NOTHING'
        )
        count = 0
        for row in rows:
            values = [serialize(row[c]) for c in cols]
            try:
                await dst_conn.execute(insert_sql, *values)
                count += 1
            except Exception as e:
                print(f"   ⚠️  Row skipped ({e}): {dict(row)}")

        print(f"   ✅  Inserted {count}/{len(rows)} rows")
    finally:
        await dst_conn.execute(f'ALTER TABLE public."{table}" ENABLE TRIGGER ALL')

    # Sync sequences so next INSERT gets the right id
    await dst_conn.execute(
        f"""
        SELECT setval(
            pg_get_serial_sequence('public."{table}"', 'id'),
            COALESCE(MAX(id), 1)
        ) FROM public."{table}"
        """
    )


async def main():
    # ── Preflight checks ─────────────────────────────────────────────────────
    print("🔍  Checking connectivity …")
    check_port("aws-1-ap-south-1.pooler.supabase.com", 5432, "Supabase")
    print("   ✅  Supabase is reachable")
    check_port("localhost", 5432, "Docker Postgres")
    print("   ✅  Docker Postgres is reachable")

    # ── Connect ──────────────────────────────────────────────────────────────
    print("\n🔌  Connecting to Supabase …")
    src_conn = await asyncpg.connect(SUPABASE_DSN, ssl="require", timeout=20)
    print("✅  Connected to Supabase")

    print("🔌  Connecting to Docker Postgres …")
    # ssl=False — local Docker postgres doesn't use SSL
    dst_conn = await asyncpg.connect(DOCKER_DSN, ssl=False, timeout=10)
    print("✅  Connected to Docker Postgres")

    try:
        for table in TABLES:
            await migrate_table(src_conn, dst_conn, table)

        print("\n\n🎉  Migration complete!")
        print("   All data has been copied from Supabase → Docker PostgreSQL.")
    finally:
        await src_conn.close()
        await dst_conn.close()


if __name__ == "__main__":
    asyncio.run(main())
