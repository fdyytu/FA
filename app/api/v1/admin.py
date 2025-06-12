"""
Admin router - minimal implementation untuk testing
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/dashboard")
async def get_dashboard():
    """Get admin dashboard"""
    return {"message": "Admin dashboard endpoint"}

@router.get("/users")
async def get_users():
    """Get all users"""
    return {"message": "Admin users endpoint"}
