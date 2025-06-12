"""
Wallet router - minimal implementation untuk testing
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/balance")
async def get_balance():
    """Get wallet balance"""
    return {"message": "Wallet balance endpoint"}

@router.post("/topup")
async def topup():
    """Topup wallet"""
    return {"message": "Topup endpoint"}
