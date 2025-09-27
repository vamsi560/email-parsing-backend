import os
import json
import logging
import re
from typing import Dict, Any
import google.generativeai as genai

logger = logging.getLogger(__name__)

# Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1000"))

# Initialize Gemini client
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(GEMINI_MODEL)
else:
    model = None

def extract_with_llm(text: str) -> Dict[str, Any]:
    """
    Extract structured insurance submission data from text using Gemini
    Returns a dictionary with the extracted fields
    """
    if not model:
        raise ValueError("Gemini API key not configured")
    
    # Truncate text if too long (keep within token limits)
    max_text_length = 30000  # Gemini has higher token limits
    if len(text) > max_text_length:
        text = text[:max_text_length] + "...[truncated]"
        logger.warning("Text truncated due to length")
    
    prompt = f"""You are an expert insurance submission data extractor. 
    Your task is to extract key information from insurance-related documents and emails.
    
    Always return a valid JSON object with exactly these fields:
    - insured_name: The name of the insured party/company
    - policy_type: Type of insurance policy (e.g., "General Liability", "Property", "Auto", "Workers Comp")
    - coverage_amount: The coverage amount/limit (e.g., "$1,000,000", "1M", etc.)
    - effective_date: Policy effective date (in YYYY-MM-DD format if possible)
    - broker: Name of the insurance broker or agent
    
    If a field cannot be determined from the text, use "Not specified" as the value.
    Return ONLY the JSON object, no additional text.
    
    Extract insurance submission information from the following text:
    
    {text}
    
    Return the data as a JSON object with the required fields:"""
    
    try:
        # Configure generation parameters
        generation_config = genai.types.GenerationConfig(
            temperature=0.1,  # Low temperature for consistent extraction
            max_output_tokens=MAX_TOKENS,
        )
        
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        content = response.text
        logger.info("Gemini extraction successful")
        
        # Parse the JSON response
        try:
            extracted_data = json.loads(content)
            
            # Validate required fields
            required_fields = ["insured_name", "policy_type", "coverage_amount", "effective_date", "broker"]
            for field in required_fields:
                if field not in extracted_data:
                    extracted_data[field] = "Not specified"
            
            return extracted_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response as JSON: {e}")
            # Try to extract JSON from the response using regex
            return extract_json_from_text(content)
            
    except Exception as e:
        logger.error(f"Gemini API call failed: {str(e)}")
        raise Exception(f"Gemini extraction failed: {str(e)}")

def extract_json_from_text(text: str) -> Dict[str, Any]:
    """
    Fallback method to extract JSON from text using regex
    """
    try:
        # Look for JSON-like structure in the text
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            return json.loads(json_str)
        else:
            # If no JSON found, return default structure
            logger.warning("No JSON found in LLM response, returning default structure")
            return {
                "insured_name": "Not specified",
                "policy_type": "Not specified", 
                "coverage_amount": "Not specified",
                "effective_date": "Not specified",
                "broker": "Not specified"
            }
    except Exception as e:
        logger.error(f"Failed to extract JSON from text: {e}")
        # Return default structure as last resort
        return {
            "insured_name": "Not specified",
            "policy_type": "Not specified",
            "coverage_amount": "Not specified", 
            "effective_date": "Not specified",
            "broker": "Not specified"
        }

def validate_extraction(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and clean the extracted data
    """
    # Ensure all required fields exist
    required_fields = ["insured_name", "policy_type", "coverage_amount", "effective_date", "broker"]
    
    for field in required_fields:
        if field not in data or not data[field] or data[field].strip() == "":
            data[field] = "Not specified"
    
    # Clean up the data
    for field in data:
        if isinstance(data[field], str):
            data[field] = data[field].strip()
    
    return data

# Alternative LLM providers (for future use)
def extract_with_openai(text: str) -> Dict[str, Any]:
    """Alternative implementation for OpenAI"""
    # Implementation for OpenAI would go here
    raise NotImplementedError("OpenAI implementation not yet available")

def extract_with_azure_openai(text: str) -> Dict[str, Any]:
    """Alternative implementation for Azure OpenAI"""
    # Implementation for Azure OpenAI would go here
    raise NotImplementedError("Azure OpenAI implementation not yet available")