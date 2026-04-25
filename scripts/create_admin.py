
import asyncio
import sys
import os

# Add backend directory to python path
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from app.db.session import SessionLocal
from app.crud.user import get_user_by_email, update_user
from app.schemas.user import UserUpdate

async def make_admin(email: str):
    async with SessionLocal() as db:
        user = await get_user_by_email(db, email=email)
        if not user:
            print(f"User {email} not found.")
            return

        # Initialize UserUpdate with role
        # Since Schema doesn't have role in Update yet, we might need to update model directly or update Schema.
        # Let's update model directly for script simplicity or update schema first.
        # Actually standard crud update uses dict from schema.
        # UserUpdate schema in `backend/app/schemas/user.py` likely doesn't have `role`.
        # I'll update the user object directly.
        user.role = "admin"
        db.add(user)
        await db.commit()
        print(f"User {email} is now an ADMIN.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python create_admin.py <email>")
        sys.exit(1)
    
    email = sys.argv[1]
    asyncio.run(make_admin(email))
