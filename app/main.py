import os
import base64
import logging
import uuid
from datetime import datetime
from typing import List, Optional

# Load environment variables first
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db, init_db
from app.models import Submission, SubmissionDraft
from app.parsers import parse_attachment
from app.llm import extract_with_llm, validate_extraction

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Ensure upload directory exists (Vercel compatible)
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/tmp/uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Pydantic Schemas
class AttachmentPayload(BaseModel):
    filename: str = Field(..., description="Name of the attachment file")
    contentBase64: str = Field(..., description="Base64 encoded file content")

class EmailIntakePayload(BaseModel):
    subject: str = Field(..., description="Email subject line")
    from_: str = Field(..., alias="from", description="Email sender address")
    received_at: str = Field(..., description="Email received timestamp")
    body: str = Field(..., description="Email body content")
    attachments: List[AttachmentPayload] = Field(default=[], description="List of email attachments")

class SubmissionDraftResponse(BaseModel):
    id: int
    sender_email: str
    subject: str
    body_text: Optional[str]
    extracted_fields: dict
    created_at: datetime
    submission_ref: str
    
    class Config:
        from_attributes = True

class ConfirmSubmissionRequest(BaseModel):
    extracted_json: Optional[dict] = Field(None, description="Updated extracted data if modified by user")

class ConfirmResponse(BaseModel):
    submission_id: int
    work_item_id: int
    assigned_underwriter: str

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None

# Initialize database on startup
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing database...")
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise
    yield
    # Shutdown
    logger.info("Application shutting down...")

# Create FastAPI app
app = FastAPI(
    title="Underwriting Workbench API",
    description="Backend API for processing insurance submissions from emails",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure as needed for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# Main API Endpoints
@app.post("/api/email/intake", response_model=dict)
async def email_intake(payload: EmailIntakePayload, db: Session = Depends(get_db)):
    """
    Process incoming email with attachments from Logic Apps
    """
    logger.info(f"Received email intake: '{payload.subject}' from {payload.from_}")
    
    try:
        # Generate unique submission reference
        import uuid
        submission_ref = uuid.uuid4()

        # Process attachments
        all_text_parts = [payload.body] if payload.body else []
        processed_files = []
        
        for attachment in payload.attachments:
            try:
                # Generate unique filename to avoid conflicts
                filename = f"{uuid.uuid4()}_{attachment.filename}"
                file_path = os.path.join(UPLOAD_DIR, filename)
                
                # Decode and save attachment
                with open(file_path, "wb") as f:
                    f.write(base64.b64decode(attachment.contentBase64))
                
                logger.info(f"Saved attachment: {file_path}")
                processed_files.append(file_path)
                
                # Parse attachment content
                text_content = parse_attachment(file_path)
                if text_content.strip():
                    all_text_parts.append(f"\n--- Content from {attachment.filename} ---\n{text_content}")
                    logger.info(f"Extracted {len(text_content)} characters from {attachment.filename}")
                else:
                    logger.warning(f"No text extracted from {attachment.filename}")
                    
            except Exception as e:
                logger.error(f"Failed to process attachment {attachment.filename}: {str(e)}")
                # Continue processing other attachments
                continue

        # Combine all text content
        combined_text = "\n".join(all_text_parts)
        logger.info(f"Combined text length: {len(combined_text)} characters")

        if not combined_text.strip():
            raise HTTPException(
                status_code=400, 
                detail="No text content could be extracted from email or attachments"
            )

        # Extract structured data using LLM
        try:
            extracted_json = extract_with_llm(combined_text)
            extracted_json = validate_extraction(extracted_json)
            logger.info("LLM extraction completed successfully")
        except Exception as e:
            logger.error(f"LLM extraction failed: {str(e)}")
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to extract structured data: {str(e)}"
            )

        # Save submission draft
        draft = SubmissionDraft(
            sender_email=payload.from_,
            subject=payload.subject,
            body_text=payload.body,
            extracted_fields=extracted_json,
            created_at=datetime.utcnow(),
            submission_ref=submission_ref
        )
        db.add(draft)
        db.commit()
        db.refresh(draft)
        
        logger.info(f"Created submission draft with ID: {draft.id}")

        return {
            "success": True,
            "draft_id": draft.id,
            "submission_ref": str(submission_ref),
            "extracted_data": extracted_json,
            "processed_attachments": len(processed_files)
        }

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error in email intake: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/api/submissions/draft/{draft_id}", response_model=SubmissionDraftResponse)
async def get_draft(draft_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a submission draft by ID
    """
    logger.info(f"Retrieving draft with ID: {draft_id}")
    
    draft = db.query(SubmissionDraft).filter(SubmissionDraft.id == draft_id).first()
    if not draft:
        logger.warning(f"Draft not found: {draft_id}")
        raise HTTPException(status_code=404, detail="Draft not found")
    
    return draft

@app.post("/api/submissions/confirm/{draft_id}", response_model=ConfirmResponse)
async def confirm_submission(
    draft_id: int, 
    request: ConfirmSubmissionRequest = None,
    db: Session = Depends(get_db)
):
    """
    Confirm and finalize a submission draft
    """
    logger.info(f"Confirming submission for draft ID: {draft_id}")
    
    # Get the draft
    draft = db.query(SubmissionDraft).filter(SubmissionDraft.id == draft_id).first()
    if not draft:
        logger.warning(f"Draft not found: {draft_id}")
        raise HTTPException(status_code=404, detail="Draft not found")

    try:
        # Use updated data if provided, otherwise use original draft data
        final_data = request.extracted_json if request and request.extracted_json else draft.extracted_fields
        
        # Assign to underwriter using round-robin
        underwriters = ["alice.smith@company.com", "bob.jones@company.com", "carol.white@company.com"]
        submission_count = db.query(Submission).count()
        assigned_underwriter = underwriters[submission_count % len(underwriters)]
        
        # Create finalized submission
        submission = Submission(
            sender_email=draft.sender_email,
            subject=draft.subject,
            body_text=draft.body_text,
            extracted_fields=final_data,
            assigned_to=assigned_underwriter,
            task_status="assigned",
            created_at=datetime.utcnow(),
            submission_ref=draft.submission_ref,
            submission_id=None  # Can be set later if needed
        )
        db.add(submission)
        db.commit()
        db.refresh(submission)
        
        logger.info(f"Created submission with ID: {submission.id} assigned to {assigned_underwriter}")

        return ConfirmResponse(
            submission_id=submission.id,
            work_item_id=submission.id,  # Using submission ID as work item reference
            assigned_underwriter=assigned_underwriter
        )

    except Exception as e:
        logger.error(f"Error confirming submission: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to confirm submission: {str(e)}"
        )

# Additional utility endpoints
@app.get("/api/submissions/draft", response_model=List[SubmissionDraftResponse])
async def list_drafts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    List all submission drafts
    """
    drafts = db.query(SubmissionDraft).offset(skip).limit(limit).all()
    return drafts

@app.get("/api/submissions", response_model=List[dict])
async def list_submissions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    List all confirmed submissions
    """
    submissions = db.query(Submission).offset(skip).limit(limit).all()
    return [
        {
            "id": s.id,
            "sender_email": s.sender_email,
            "subject": s.subject,
            "extracted_fields": s.extracted_fields,
            "assigned_to": s.assigned_to,
            "task_status": s.task_status,
            "created_at": s.created_at,
            "submission_ref": str(s.submission_ref) if s.submission_ref else None
        }
        for s in submissions
    ]

@app.get("/api/work-items", response_model=List[dict])
async def list_work_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    List all work items (submissions with assigned status)
    """
    work_items = db.query(Submission).filter(Submission.task_status.isnot(None)).offset(skip).limit(limit).all()
    return [
        {
            "id": wi.id,
            "submission_ref": str(wi.submission_ref) if wi.submission_ref else None,
            "assigned_to": wi.assigned_to,
            "task_status": wi.task_status,
            "subject": wi.subject,
            "created_at": wi.created_at
        }
        for wi in work_items
    ]

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    logger.error(f"HTTP {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)