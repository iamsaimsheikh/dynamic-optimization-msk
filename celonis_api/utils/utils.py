import json

def print_debug(action: str, url: str, headers: dict = None, payload: dict = None):
    """Print debug information"""
    print("\n🔍 DEBUG: {}".format(action))
    print("📌 URL: {}".format(url))
    if headers:
        print("📄 Headers: {}".format(headers))
    if payload:
        print("📊 Payload: {}".format(json.dumps(payload, indent=2)))

def handle_response(response):
    """Handle API response and return JSON or error"""
    if response.status_code in [200, 201, 204]:
        try:
            return response.json() if response.text else {"message": "Success"}
        except json.JSONDecodeError:
            return {
                "error": "Invalid JSON response from Celonis API",
                "status_code": response.status_code,
                "response": response.text
            }
    
    return {
        "error": "Request failed with status {}".format(response.status_code),
        "status_code": response.status_code,
        "response": response.text or "No response body"
    }
