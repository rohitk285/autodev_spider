from fastapi import APIRouter
from .auth import authrouter
from .story import storyrouter

api_router = APIRouter(prefix="/api")
api_router.include_router(authrouter,prefix="/auth")
api_router.include_router(storyrouter,prefix="/story")