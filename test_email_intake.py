import requests
import json
import base64

# Test the email intake endpoint
url = "http://127.0.0.1:8000/api/email/intake"

# Sample email data
email_data = {
    "subject": "Insurance Submission - ABC Company",
    "from": "broker@insurance.com",
    "received_at": "2025-09-27T06:00:00Z",
    "body": """
    Dear Underwriter,
    
    Please find attached the insurance submission for ABC Company.
    
    Policy Details:
    - Insured: ABC Manufacturing Company
    - Policy Type: General Liability
    - Coverage Amount: $2,000,000
    - Effective Date: 2025-10-01
    - Broker: John Smith Insurance
    
    Best regards,
    John Smith
    """,
    "attachments": [
        {
            "filename": "sample.txt",
            "contentBase64": base64.b64encode(b"This is a sample attachment with insurance details.").decode()
        }
    ]
}

print("Testing email intake endpoint...")
print(f"URL: {url}")
print(f"Data: {json.dumps(email_data, indent=2)}")

try:
    response = requests.post(url, json=email_data)
    print(f"\nResponse Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        print("\n✅ Email intake successful!")
        result = response.json()
        if "draft_id" in result:
            draft_id = result["draft_id"]
            print(f"Draft ID: {draft_id}")
            
            # Test getting the draft
            draft_url = f"http://127.0.0.1:8000/api/submissions/draft/{draft_id}"
            draft_response = requests.get(draft_url)
            print(f"\nDraft retrieval: {draft_response.status_code}")
            if draft_response.status_code == 200:
                print(f"Draft data: {json.dumps(draft_response.json(), indent=2)}")
    else:
        print(f"\n❌ Email intake failed: {response.text}")
        
except Exception as e:
    print(f"Error: {e}")