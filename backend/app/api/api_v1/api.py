from fastapi import APIRouter
from app.api.api_v1.endpoints import rag, projects

api_router = APIRouter()
api_router.include_router(rag.router, prefix="/rag", tags=["rag"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
from app.api.api_v1.endpoints import documents
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
from app.api.api_v1.endpoints import models
api_router.include_router(models.router, prefix="/models", tags=["models"])
from app.api.api_v1.endpoints import usage
api_router.include_router(usage.router, prefix="/usage", tags=["usage"])
from app.api.api_v1.endpoints import admin
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
from app.api.api_v1.endpoints import users
api_router.include_router(users.router, prefix="/users", tags=["users"])
from app.api.api_v1.endpoints import feedback
api_router.include_router(feedback.router, prefix="/feedback", tags=["feedback"])

