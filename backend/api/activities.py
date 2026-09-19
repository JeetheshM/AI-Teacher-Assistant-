"""
activities.py — generates activity AND saves to Supabase materials table.
"""
import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional

from backend.database.db import get_db
from backend.models.core import Material
from backend.mocks.mock_llm_service import MockLLMService
from backend.services.gemini_llm_service import GeminiLLMService
from backend.services.activity_service import ActivityService
from backend.models.activity_models import ActivityGenerationRequest

router = APIRouter()

try:
    _activity_service = ActivityService(GeminiLLMService())
except Exception:
    _activity_service = ActivityService(MockLLMService())


class ActivityRequest(BaseModel):
    subject: str = Field(..., example="Science")
    topic: str = Field(..., example="Photosynthesis")
    grade: int = Field(..., example=8)
    duration_minutes: int = Field(default=20, example=20)
    difficulty: str = Field(default="intermediate", example="intermediate")
    group_size: Optional[int] = Field(default=4, example=4)
    lesson_id: Optional[str] = Field(default=None, description="Link activity to an existing lesson")


@router.post("/generate", response_model=dict)
async def generate_activity(request: ActivityRequest, db: Session = Depends(get_db)):
    req = ActivityGenerationRequest(
        subject=request.subject,
        topic=request.topic,
        grade=request.grade,
        duration_minutes=request.duration_minutes,
        difficulty=request.difficulty,
        activity_type="group"
    )
    activity = await _activity_service.generate_activity(req)

    # Save to Supabase materials table
    mat = Material(
        lesson_id=request.lesson_id,
        type="activity",
        title=activity.title,
        content=json.dumps(activity.model_dump()),
    )
    db.add(mat)
    db.commit()

    return activity


@router.get("/", summary="List all saved activities")
def list_activities(db: Session = Depends(get_db)):
    mats = db.query(Material).filter(Material.type == "activity").order_by(Material.created_at.desc()).limit(50).all()
    result = []
    for m in mats:
        try:
            data = json.loads(m.content)
        except Exception:
            data = {"raw": m.content}
        result.append({"id": m.id, "lesson_id": m.lesson_id, "created_at": str(m.created_at), **data})
    return result
