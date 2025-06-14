from typing import Any, Optional, Dict

def create_response(
    success: bool = True,
    message: str = "Success",
    data: Optional[Any] = None,
    errors: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create standardized API response"""
    response = {
        "success": success,
        "message": message
    }
    
    if data is not None:
        response["data"] = data
    
    if errors is not None:
        response["errors"] = errors
    
    return response
