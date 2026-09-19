"""
TeachMate AI - Development Server Entrypoint (Person 2 standalone runner).
Includes both lessons_router and simplify_router under a FastAPI application.
"""

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from backend.api.lessons_router import lessons_router
from backend.api.simplify_router import simplify_router

app = FastAPI(
    title="TeachMate AI - Lesson & Simplification AI API",
    description="Standalone development server for Person 2 (Lesson Planner + Simplification AI)",
    version="1.0.0"
)

# Mount Person 2's routers
app.include_router(lessons_router)
app.include_router(simplify_router)


@app.get("/", include_in_schema=False)
async def root():
    """Redirect root path to interactive Swagger documentation."""
    return RedirectResponse(url="/docs")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("dev_server:app", host="127.0.0.1", port=8000, reload=True)
