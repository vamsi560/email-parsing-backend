import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required. Please configure your database connection.")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)
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
    try:
        # Import all models to ensure they're registered
        from app.models import Submission, SubmissionDraft
        
        # Create all tables that don't exist
        Base.metadata.create_all(bind=engine, checkfirst=True)
        print("Database tables initialized successfully")
    except Exception as e:
        print(f"Failed to initialize database tables: {e}")
        raise