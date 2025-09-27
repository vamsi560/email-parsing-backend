def handler(request):
    import json
    from datetime import datetime
    
    # Basic response that should work
    try:
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "message": "Hello from Vercel Python!",
                "status": "working",
                "timestamp": datetime.utcnow().isoformat()
            })
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)})
        }
