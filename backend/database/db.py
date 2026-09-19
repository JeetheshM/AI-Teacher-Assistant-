import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Load local env from the backend directory so the app behaves correctly whether
# it is started from the repo root or from the backend folder.
backend_dir = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=backend_dir / ".env")
load_dotenv()

# Use SQLite by default for local development. If the Supabase placeholder values
# are still present in .env, fall back instead of trying to connect to a dead DB.
default_database_url = "sqlite:///./teachmate.db"
configured_database_url = os.getenv("DATABASE_URL", "").strip()
if not configured_database_url or "[YOUR-PASSWORD]" in configured_database_url:
    configured_database_url = default_database_url
    os.environ["DATABASE_URL"] = configured_database_url

DATABASE_URL = configured_database_url

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
