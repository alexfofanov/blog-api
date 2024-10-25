from fastapi import APIRouter

from src.api.v1.post import post_router
from src.api.v1.user import user_router

api_router = APIRouter()

api_router.include_router(user_router, prefix='/users', tags=['users'])
api_router.include_router(post_router, prefix='/posts', tags=['posts'])
