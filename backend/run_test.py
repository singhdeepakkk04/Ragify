import sys, logging
from app.api.deps import _decode_supabase_jwt
from app.core.config import settings

logging.basicConfig(level=logging.DEBUG)
print("SUPABASE_JWT_SECRET:", bool(settings.SUPABASE_JWT_SECRET))
print("SUPABASE_URL:", bool(settings.SUPABASE_URL))
try:
    token = sys.argv[1]
    print("\nResult:", _decode_supabase_jwt(token))
except Exception as e:
    print(e)
