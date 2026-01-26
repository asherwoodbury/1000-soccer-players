"""
FastAPI backend for the 1000 Soccer Players app.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import players, sessions, clubs
from app.models.database import init_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    init_database()
    yield


app = FastAPI(
    title="1000 Soccer Players",
    description="API for the soccer player guessing game",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "1000 Soccer Players API", "version": "0.1.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


# Include routers
app.include_router(players.router, prefix="/api/players", tags=["players"])
app.include_router(sessions.router, prefix="/api/sessions", tags=["sessions"])
app.include_router(clubs.router, prefix="/api/clubs", tags=["clubs"])
