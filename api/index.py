import os
import sys

# Add the root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not available in production

# Import the main FastAPI app
try:
    from app.main import app
    print("Successfully imported main app")
except Exception as e:
    print(f"Failed to import main app: {e}")
    # Create a fallback app
    from fastapi import FastAPI
    from datetime import datetime
    
    app = FastAPI(title="Email Parsing Backend - Fallback")
    
    @app.get("/")
    def root():
        return {
            "error": "Main app import failed",
            "message": f"Import error: {str(e)}",
            "fallback": True,
            "timestamp": datetime.utcnow().isoformat()
        }

# Vercel handler using Mangum
try:
    from mangum import Mangum
    handler = Mangum(app)
except ImportError as e:
    print(f"Mangum import failed: {e}")
    # Pure function fallback
    import json
    from datetime import datetime
    
    def handler(request):
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "error": "Mangum not available",
                "detail": str(e),
                "timestamp": datetime.utcnow().isoformat()
            })
        }