"""
PPOB router - minimal implementation untuk testing
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/products")
async def get_products():
    """Get PPOB products"""
    return {"message": "PPOB products endpoint"}

@router.post("/purchase")
async def purchase():
    """Purchase PPOB product"""
    return {"message": "PPOB purchase endpoint"}
