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

router = APIRouter()


class ActivityRequest(BaseModel):
    subject: str = Field(..., example="Science")
    topic: str = Field(..., example="Photosynthesis")
    grade: int = Field(..., example=8)
    duration_minutes: int = Field(default=20, example=20)
    difficulty: str = Field(default="intermediate", example="intermediate")
    group_size: Optional[int] = Field(default=4, example=4)
    lesson_id: Optional[str] = Field(default=None, description="Link activity to an existing lesson")


class ActivityResponse(BaseModel):
    title: str
    objective: str
    duration_minutes: int
    group_size: int
    materials: List[str]
    instructions: List[str]
    teacher_role: str
    expected_outcome: str
    assessment_method: str


@router.post("/generate", response_model=ActivityResponse)
def generate_activity(request: ActivityRequest, db: Session = Depends(get_db)):
    activity = ActivityResponse(
        title=f"Interactive {request.topic} Exploration",
        objective=f"Hands-on activity for grade {request.grade} students to understand {request.topic}.",
        duration_minutes=request.duration_minutes,
        group_size=request.group_size or 4,
        materials=[
            "Whiteboard and markers",
            "Concept diagram worksheets",
            "Colored sticky notes",
        ],
        instructions=[
            "Divide the classroom into small groups of 4.",
            "Distribute worksheets and sticky notes to each group.",
            "Ask students to map out the key inputs and outputs of the process.",
            "Have each group present their diagram to the rest of the class.",
        ],
        teacher_role="Facilitator – walk around to guide discussions and clarify misconceptions.",
        expected_outcome=f"Students actively map and present the core concepts of {request.topic}.",
        assessment_method="Peer review & Group presentation check.",
    )

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
