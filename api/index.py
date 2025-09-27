import json
from datetime import datetime
from urllib.parse import parse_qs

def handler(request, context=None):
    """
    Pure Python handler function for Vercel
    """
    try:
        # Get request details
        method = request.get('httpMethod', 'GET')
        path = request.get('path', '/')
        body = request.get('body', '{}')
        
        # Parse JSON body for POST requests
        if method == 'POST' and body:
            try:
                if isinstance(body, str):
                    payload = json.loads(body)
                else:
                    payload = body
            except json.JSONDecodeError:
                payload = {}
        else:
            payload = {}
        
        # Route handling
        if path == '/' and method == 'GET':
            response_data = {
                "message": "Email Parsing Backend is working!",
                "status": "ok", 
                "timestamp": datetime.utcnow().isoformat(),
                "endpoints": ["/", "/api/email/intake"]
            }
            
        elif path == '/api/email/intake' and method == 'POST':
            # Email intake logic
            response_data = {
                "success": True,
                "message": "Email processed successfully",
                "received_data": {
                    "subject": payload.get("subject", "not provided"),
                    "from": payload.get("from", "not provided"),
                    "body_length": len(payload.get("body", "")),
                    "attachments_count": len(payload.get("attachments", []))
                },
                "mock_extracted_data": {
                    "insured_name": "Test Insurance Company",
                    "policy_type": "General Liability",
                    "coverage_amount": "$1,000,000",
                    "effective_date": "2025-10-01",
                    "broker": "Sample Broker LLC"
                },
                "processed_attachments": len(payload.get("attachments", [])),
                "note": "This is a working mock response from Vercel"
            }
            
        else:
            # 404 for unknown routes
            response_data = {
                "error": "Not found",
                "path": path,
                "method": method
            }
            return {
                "statusCode": 404,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps(response_data)
            }
        
        # Success response
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            },
            "body": json.dumps(response_data)
        }
        
    except Exception as e:
        # Error response
        error_data = {
            "error": "Internal server error",
            "detail": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps(error_data)
        }
