"""
Application entrypoint. Run with: uvicorn app.main:app --reload
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.database import Base, engine
from app.routers import list_router, search_router, suggestions_router, voice_router

settings = get_settings()

# Creates tables on startup if they don't exist. Fine for SQLite/small
# projects; a real production service would use Alembic migrations instead
# (noted in README as a next step).
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    description="Voice-driven shopping list manager with smart suggestions.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(list_router.router)
app.include_router(voice_router.router)
app.include_router(suggestions_router.router)
app.include_router(search_router.router)


@app.get("/api/health", tags=["health"])
def health_check():
    """Used by the frontend to show a connection status, and by the hosting
    platform's health probe."""
    return {"status": "ok", "app": settings.app_name}
