import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

print("Testing with gemini-2.5-flash model...")
try:
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content("Hello, can you extract structured data from insurance documents?")
    print("✅ gemini-2.5-flash works!")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"❌ gemini-2.5-flash failed: {e}")