from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database.db import engine, Base
from backend.api import lessons, quizzes, activities, documents, simplify

# Create tables locally (for SQLite fallback). For Supabase, use schema.sql in the SQL Editor.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="TeachMate AI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # MVP only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(lessons.router, prefix="/api/lessons", tags=["Lessons"])
app.include_router(quizzes.router, prefix="/api/quizzes", tags=["Quizzes"])
app.include_router(activities.router, prefix="/api/activities", tags=["Activities"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(simplify.router, prefix="/api/simplify", tags=["Simplify"])

@app.get("/")
def read_root():
    return {"message": "TeachMate AI Backend is running!"}
