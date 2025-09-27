from sqlalchemy import Column, Integer, String, DateTime, JSON, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
import uuid

Base = declarative_base()

class Submission(Base):
    """Model matching existing submissions table in Retool database"""
    __tablename__ = "submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    assigned_to = Column(Text, nullable=True)  # matches 'text' type
    body_text = Column(Text, nullable=True)    # matches 'text' type  
    created_at = Column(DateTime, nullable=True)  # matches 'timestamp' type
    extracted_fields = Column(JSON, nullable=True)  # matches 'jsonb' type
    sender_email = Column(Text, nullable=True)   # matches 'text' type
    subject = Column(Text, nullable=True)        # matches 'text' type
    submission_id = Column(Integer, nullable=True)  # matches 'integer' type
    submission_ref = Column(UUID(as_uuid=True), default=uuid.uuid4, nullable=True)  # matches 'uuid' type
    task_status = Column(Text, nullable=True)    # matches 'text' type

# Optional: Keep draft table for temporary storage before final submission
class SubmissionDraft(Base):
    """Temporary storage for LLM extracted data before confirmation"""
    __tablename__ = "submission_draft"
    
    id = Column(Integer, primary_key=True, index=True)
    sender_email = Column(Text, nullable=False)
    subject = Column(Text, nullable=False)
    body_text = Column(Text, nullable=True)
    extracted_fields = Column(JSON, nullable=False)
    created_at = Column(DateTime, nullable=False)
    submission_ref = Column(UUID(as_uuid=True), default=uuid.uuid4, nullable=False)