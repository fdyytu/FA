"""
Controller untuk domain game
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.domains.game.services.game_service import GameValidationService, GameProductService
from app.domains.game.schemas.game_schemas import (
    GameValidationRequest, GameValidationResponse, GameCategoryResponse, GameProductResponse
)

router = APIRouter(prefix="/api/v1/game", tags=["Game"])

@router.get("/categories", response_model=List[dict])
async def get_game_categories(db: Session = Depends(get_db)):
    """Ambil semua kategori game"""
    try:
        service = GameProductService(db)
        categories = service.get_game_categories()
        return {"success": True, "data": categories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/products/{game_code}", response_model=List[dict])
async def get_game_products(game_code: str, db: Session = Depends(get_db)):
    """Ambil produk berdasarkan kode game"""
    try:
        service = GameProductService(db)
        products = service.get_products_by_game(game_code.upper())
        return {"success": True, "data": products}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/validate", response_model=GameValidationResponse)
async def validate_game_account(request: GameValidationRequest):
    """Validasi akun game"""
    try:
        service = GameValidationService()
        result = await service.validate_game_account(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/price/{game_code}")
async def get_game_prices(game_code: str, db: Session = Depends(get_db)):
    """Ambil daftar harga produk game untuk Discord bot"""
    try:
        service = GameProductService(db)
        products = service.get_products_by_game(game_code.upper())
        
        if not products:
            return {"success": False, "message": f"Game {game_code} tidak ditemukan"}
        
        price_list = []
        for product in products:
            price_list.append(f"• {product['name']}: Rp {product['price']:,.0f}")
        
        return {
            "success": True,
            "game": game_code.upper(),
            "prices": "\n".join(price_list)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
