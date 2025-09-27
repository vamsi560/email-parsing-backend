import json
from datetime import datetime

def handler(request):
    """
    Vercel-compatible handler function
    """
    try:
        # Get the request path and method
        path = request.get("path", "/")
        method = request.get("httpMethod", "GET")
        
        # Route handling
        if path == "/" and method == "GET":
            response_body = {
                "message": "Email Parsing Backend is working!",
                "status": "ok",
                "timestamp": datetime.utcnow().isoformat()
            }
        elif path == "/health" and method == "GET":
            response_body = {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat()
            }
        elif path == "/api/email/intake" and method == "POST":
            # Parse request body
            body = request.get("body", "{}")
            if isinstance(body, str):
                try:
                    data = json.loads(body)
                except:
                    data = {}
            else:
                data = body
            
            response_body = {
                "success": True,
                "message": "Email intake successful",
                "received_data": {
                    "subject": data.get("subject", "not provided"),
                    "from": data.get("from", "not provided"),
                    "body_length": len(data.get("body", "")),
                    "attachments_count": len(data.get("attachments", []))
                },
                "extracted_data": {
                    "insured_name": "Test Company Inc",
                    "policy_type": "General Liability",
                    "coverage_amount": "$1,000,000",
                    "effective_date": "2025-10-01",
                    "broker": "Test Broker LLC"
                }
            }
        else:
            response_body = {
                "error": "Not found",
                "path": path,
                "method": method
            }
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(response_body)
            }
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            },
            "body": json.dumps(response_body)
        }
        
    except Exception as e:
        error_response = {
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(error_response)
        }