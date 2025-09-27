import os
import sys

# Add the root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

try:
    from app.main import app
except ImportError as e:
    # Fallback for debugging
    print(f"Import error: {e}")
    from fastapi import FastAPI
    from datetime import datetime
    
    app = FastAPI(title="Email Parsing Backend - Fallback")
    
    @app.get("/")
    def root():
        return {
            "error": f"Import failed: {str(e)}",
            "message": "Fallback app is running",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @app.get("/health")
    def health():
        return {"status": "fallback", "error": str(e)}

# For Vercel compatibility
from mangum import Mangum
handler = Mangum(app)