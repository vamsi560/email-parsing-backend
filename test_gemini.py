import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

print("Available Gemini models:")
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"- {model.name}")

print("\nTesting with gemini-pro model...")
try:
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content("Hello, can you extract structured data?")
    print("✅ gemini-pro works!")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"❌ gemini-pro failed: {e}")

print("\nTesting with models/gemini-pro model...")
try:
    model = genai.GenerativeModel('models/gemini-pro')
    response = model.generate_content("Hello, can you extract structured data?")
    print("✅ models/gemini-pro works!")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"❌ models/gemini-pro failed: {e}")