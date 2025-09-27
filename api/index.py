from fastapi import FastAPI
from mangum import Mangum
from datetime import datetime

app = FastAPI(title="Hello Vercel FastAPI")

@app.get("/")
def root():
    return {
        "message": "Hello from FastAPI on Vercel!",
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/email/intake")
def email_intake(payload: dict):
    """
    Mock email intake endpoint for testing Logic Apps → Vercel integration.
    """
    return {
        "success": True,
        "received_subject": payload.get("subject"),
        "received_from": payload.get("from"),
        "attachments_count": len(payload.get("attachments", [])),
        "note": "This is a mock response from Vercel."
    }

# Required by Vercel
handler = Mangum(app)
