from __future__ import annotations

import logging
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


def get_supabase_client():
    """Create a Supabase client (service role) if configured; else return None."""
    supabase_url = (getattr(settings, "SUPABASE_URL", "") or "").strip()
    supabase_key = (getattr(settings, "SUPABASE_KEY", "") or "").strip()
    if not supabase_url or not supabase_key:
        return None

    try:
        from supabase import create_client

        return create_client(supabase_url, supabase_key)
    except Exception as e:
        logger.warning(f"[Supabase] Client init failed: {e}")
        return None
