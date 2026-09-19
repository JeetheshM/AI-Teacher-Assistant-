from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database.db import engine, Base
from backend.api.lessons_router import lessons_router
from backend.api.simplify_router import simplify_router
from backend.api import quizzes, activities, documents

# Create tables locally (for SQLite fallback). For Supabase, schema.sql has created them.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="TeachMate AI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # MVP only
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
    return {"message": "TeachMate AI Backend is running with integrated AI modules!"}
