import asyncio
from app.api.deps import _decode_supabase_jwt
from app.core.config import settings

token = input("Paste token: ")
print("\nSettings:")
print("SUPABASE_JWT_SECRET:", bool(settings.SUPABASE_JWT_SECRET))
print("SUPABASE_URL:", bool(settings.SUPABASE_URL))
print("\nDecoding...")
res = _decode_supabase_jwt(token)
print("Result:", res)
