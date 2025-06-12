"""
Authentication router - minimal implementation untuk testing
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/test")
async def test_auth():
    """Test endpoint untuk auth"""
    return {"message": "Auth router working"}

@router.post("/login")
async def login():
    """Login endpoint placeholder"""
    return {"message": "Login endpoint"}

@router.post("/register")
async def register():
    """Register endpoint placeholder"""
    return {"message": "Register endpoint"}
