from sqlalchemy import Column, String, Integer, Text, ForeignKey, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database.db import Base, DATABASE_URL
import uuid

def generate_uuid():
    return str(uuid.uuid4())

# Use PostgreSQL native UUID for Supabase, String(36) for SQLite fallback
def _uuid_col(primary_key=False, fk=None, nullable=True):
    """Create a UUID column that returns strings in both SQLite and PostgreSQL."""
    if "sqlite" in DATABASE_URL:
        if fk:
            return Column(String(36), ForeignKey(fk, ondelete="CASCADE"), nullable=nullable)
        return Column(String(36), primary_key=primary_key, default=generate_uuid, nullable=nullable)
    else:
        # PostgreSQL/Supabase: use native UUID type but return as Python str
        if fk:
            return Column(PG_UUID(as_uuid=False), ForeignKey(fk, ondelete="CASCADE"), nullable=nullable)
        return Column(PG_UUID(as_uuid=False), primary_key=primary_key, default=generate_uuid, nullable=nullable)


class Lesson(Base):
    __tablename__ = "lessons"

    id = _uuid_col(primary_key=True)
    title = Column(String(255))
    subject = Column(String(255), nullable=False)
    topic = Column(String(255), nullable=False)
    grade = Column(Integer, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    difficulty = Column(String(50), nullable=False)
    learning_objective = Column(Text)
    status = Column(String(50), default='draft')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    documents = relationship("Document", back_populates="lesson", cascade="all, delete-orphan")
    materials = relationship("Material", back_populates="lesson", cascade="all, delete-orphan")
    quizzes = relationship("Quiz", back_populates="lesson", cascade="all, delete-orphan")
    generation_logs = relationship("GenerationLog", back_populates="lesson", cascade="all, delete-orphan")


class Document(Base):
    __tablename__ = "documents"

    id = _uuid_col(primary_key=True)
    lesson_id = _uuid_col(fk="lessons.id")
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50))
    storage_path = Column(Text)
    status = Column(String(50), default='processed')
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    lesson = relationship("Lesson", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = _uuid_col(primary_key=True)
    document_id = _uuid_col(fk="documents.id")
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    page_number = Column(Integer)
    embedding_reference = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    document = relationship("Document", back_populates="chunks")


class Material(Base):
    __tablename__ = "materials"

    id = _uuid_col(primary_key=True)
    lesson_id = _uuid_col(fk="lessons.id")
    type = Column(String(50), nullable=False)
    title = Column(String(255))
    content = Column(Text, nullable=False)
    version = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    lesson = relationship("Lesson", back_populates="materials")


class Quiz(Base):
    __tablename__ = "quizzes"

    id = _uuid_col(primary_key=True)
    lesson_id = _uuid_col(fk="lessons.id")
    title = Column(String(255))
    difficulty = Column(String(50))
    question_count = Column(Integer)
    status = Column(String(50), default='generated')
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    lesson = relationship("Lesson", back_populates="quizzes")
    questions = relationship("Question", back_populates="quiz", cascade="all, delete-orphan")


class Question(Base):
    __tablename__ = "questions"

    id = _uuid_col(primary_key=True)
    quiz_id = _uuid_col(fk="quizzes.id")
    question_text = Column(Text, nullable=False)
    question_type = Column(String(50), nullable=False)
    difficulty = Column(String(50))
    bloom_level = Column(String(50))
    options_json = Column(JSON)
    correct_answer = Column(Text, nullable=False)
    explanation = Column(Text)
    validation_status = Column(String(50), default='pending')

    quiz = relationship("Quiz", back_populates="questions")


class GenerationLog(Base):
    __tablename__ = "generation_logs"

    id = _uuid_col(primary_key=True)
    lesson_id = _uuid_col(fk="lessons.id")
    feature = Column(String(100))
    model = Column(String(100))
    prompt_version = Column(String(50))
    status = Column(String(50))
    latency_ms = Column(Integer)
    input_tokens = Column(Integer)
    output_tokens = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    lesson = relationship("Lesson", back_populates="generation_logs")
