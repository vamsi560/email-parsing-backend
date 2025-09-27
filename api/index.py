import os
import sys
import base64
import logging
import uuid
from datetime import datetime
from typing import List, Optional

# Add the root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not available in production

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Underwriting Workbench API",
    description="Backend API for processing insurance submissions from emails",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# Import modules with error handling
try:
    from app.database import get_db, init_db
    from app.models import SubmissionDraft
    from app.parsers import parse_attachment
    from app.llm import extract_with_llm, validate_extraction
    FULL_FUNCTIONALITY = True
    
    # Initialize database
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        FULL_FUNCTIONALITY = False
        
except Exception as e:
    logger.error(f"Failed to import app modules: {e}")
    FULL_FUNCTIONALITY = False

# Routes
@app.get("/")
def root():
    return {
        "message": "Underwriting Workbench API",
        "version": "1.0.0",
        "status": "running",
        "full_functionality": FULL_FUNCTIONALITY,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "full_functionality": FULL_FUNCTIONALITY,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/email/intake")
def email_intake(payload: EmailIntakePayload):
    """
    Process incoming email with attachments from Logic Apps
    """
    logger.info(f"Received email intake: '{payload.subject}' from {payload.from_}")
    
    if not FULL_FUNCTIONALITY:
        # Return mock response when full functionality isn't available
        return {
            "success": True,
            "message": "Mock response - full functionality not available",
            "draft_id": 999,
            "submission_ref": str(uuid.uuid4()),
            "extracted_data": {
                "insured_name": "Mock Company Inc",
                "policy_type": "General Liability",
                "coverage_amount": "$1,000,000",
                "effective_date": "2025-10-01",
                "broker": "Mock Insurance Broker"
            },
            "processed_attachments": len(payload.attachments),
            "note": "This is a mock response. Database and LLM not configured."
        }
    
    try:
        # Get database session
        db_session = next(get_db())
        
        # Generate unique submission reference
        submission_ref = uuid.uuid4()
        
        # Ensure upload directory exists
        upload_dir = os.getenv("UPLOAD_DIR", "/tmp/uploads")
        os.makedirs(upload_dir, exist_ok=True)

        # Process attachments
        all_text_parts = [payload.body] if payload.body else []
        processed_files = []
        
        for attachment in payload.attachments:
            try:
                # Generate unique filename to avoid conflicts
                filename = f"{uuid.uuid4()}_{attachment.filename}"
                file_path = os.path.join(upload_dir, filename)
                
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
        db_session.add(draft)
        db_session.commit()
        db_session.refresh(draft)
        
        logger.info(f"Created submission draft with ID: {draft.id}")

        return {
            "success": True,
            "draft_id": draft.id,
            "submission_ref": str(submission_ref),
            "extracted_data": extracted_json,
            "processed_attachments": len(processed_files)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in email intake: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
    finally:
        if 'db_session' in locals():
            db_session.close()

# Vercel handler
from mangum import Mangum
handler = Mangum(app)