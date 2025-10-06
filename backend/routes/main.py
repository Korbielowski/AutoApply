from fastapi import APIRouter

from backend.routes import pages, users

api_router = APIRouter()
api_router.include_router(pages.router)
api_router.include_router(users.router)
