import os
import sys

# Add the root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from app.main import app

# Vercel serverless function handler
def handler(request, response):
    return app

# For Vercel compatibility
app = app