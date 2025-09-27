import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables (only creates tables that don't exist)"""
    # Only create the draft table since submissions table already exists
    from app.models import SubmissionDraft
    SubmissionDraft.__table__.create(bind=engine, checkfirst=True)