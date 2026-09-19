import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent / ".env")
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database.db import engine, Base, DATABASE_URL
from backend.api.lessons_router import router as lessons_router
from backend.api.simplify_router import router as simplify_router
from backend.api import quizzes, activities, documents

# Only create tables for SQLite (local fallback).
# For Supabase (PostgreSQL), tables already exist via schema.sql run in Supabase SQL Editor.
if "sqlite" in DATABASE_URL:
    Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TeachMate AI API",
    version="1.0.0",
    description="TeachMate AI — Teacher Assistant Backend",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # MVP only — tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(lessons_router)
app.include_router(simplify_router)
app.include_router(quizzes.router, prefix="/api/quizzes", tags=["Quizzes"])
app.include_router(activities.router, prefix="/api/activities", tags=["Activities"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])


@app.get("/")
def read_root():
    db_type = "Supabase (PostgreSQL)" if "supabase" in DATABASE_URL else "SQLite (local)"
    return {
        "status": "ok",
        "message": "TeachMate AI Backend is running!",
        "database": db_type,
    }


@app.get("/health")
@app.get("/api/health")
def health_check():
    db_type = "supabase" if "supabase" in DATABASE_URL else "sqlite"
    return {"status": "ok", "service": "TeachMate AI", "db": db_type}
