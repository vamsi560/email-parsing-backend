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
    app = FastAPI()
    
    @app.get("/")
    def root():
        return {"error": f"Import failed: {str(e)}"}

# For Vercel compatibility - this is the handler Vercel will call
def handler(request):
    from mangum import Mangum
    asgi_handler = Mangum(app)
    return asgi_handler(request, {})