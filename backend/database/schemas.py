from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime

# Common Request Contract from Spec
class BaseGenerationRequest(BaseModel):
    subject: str
    topic: str
    grade: int
    duration_minutes: int
    difficulty: str
    learning_objective: str
    document_id: Optional[str] = None

# Lesson schemas
class LessonCreate(BaseGenerationRequest):
    pass

class LessonResponse(BaseGenerationRequest):
    id: str
    title: Optional[str]
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Quiz schemas
class QuestionSchema(BaseModel):
    question: str
    type: str
    difficulty: str
    bloom_level: Optional[str] = None
    options: List[str] = []
    correct_answer: str
    explanation: Optional[str] = None

class QuizCreate(BaseModel):
    lesson_id: str
    questions: List[QuestionSchema]

# Generic response message
class MessageResponse(BaseModel):
    success: bool
    message: str
    error: Optional[str] = None
