from fastapi import FastAPI
from datetime import datetime

# Create a minimal FastAPI app
app = FastAPI(title="Email Parsing Backend")

@app.get("/")
def root():
    return {
        "message": "Email Parsing Backend is working!",
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

# Vercel handler
from mangum import Mangum
handler = Mangum(app)