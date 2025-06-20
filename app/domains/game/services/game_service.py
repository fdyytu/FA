"""
Service untuk domain game dan validasi akun
"""
import asyncio
import aiohttp
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from app.domains.game.repositories.game_repository import GameCategoryRepository, GameProductRepository
from app.domains.game.schemas.game_schemas import (
    GameValidationRequest, GameValidationResponse, GameTopupRequest
)

class GameValidationService:
    """Service untuk validasi akun game"""
    
    # Mapping game codes ke API endpoints
    GAME_APIS = {
        'ML': 'https://api.mobilelegends.com/v1/check',
        'FF': 'https://api.freefire.com/v1/check', 
        'PUBG': 'https://api.pubgmobile.com/v1/check',
        'GENSHIN': 'https://api.genshin.com/v1/check'
    }
    
    async def validate_game_account(self, request: GameValidationRequest) -> GameValidationResponse:
        """Validasi akun game berdasarkan game code"""
        try:
            if request.game_code == 'ML':
                return await self._validate_mobile_legends(request)
            elif request.game_code == 'FF':
                return await self._validate_free_fire(request)
            elif request.game_code == 'PUBG':
                return await self._validate_pubg_mobile(request)
            elif request.game_code == 'GENSHIN':
                return await self._validate_genshin_impact(request)
            else:
                return GameValidationResponse(
                    user_id=request.user_id,
                    server_id=request.server_id,
                    is_valid=False,
                    message=f"Game {request.game_code} belum didukung"
                )
        except Exception as e:
            return GameValidationResponse(
                user_id=request.user_id,
                server_id=request.server_id,
                is_valid=False,
                message=f"Error validasi: {str(e)}"
            )
    
    async def _validate_mobile_legends(self, request: GameValidationRequest) -> GameValidationResponse:
        """Validasi akun Mobile Legends"""
        # Simulasi validasi ML (implementasi sebenarnya perlu API ML)
        if len(request.user_id) >= 6 and request.user_id.isdigit():
            return GameValidationResponse(
                user_id=request.user_id,
                server_id=request.server_id or "ID",
                nickname=f"Player_{request.user_id[-4:]}",
                is_valid=True,
                message="Akun Mobile Legends valid"
            )
        return GameValidationResponse(
            user_id=request.user_id,
            server_id=request.server_id,
            is_valid=False,
            message="User ID Mobile Legends tidak valid"
        )

class GameProductService:
    """Service untuk manajemen produk game"""
    
    def __init__(self, db: Session):
        self.db = db
        self.category_repo = GameCategoryRepository(db)
        self.product_repo = GameProductRepository(db)
    
    def get_game_categories(self) -> List[Dict]:
        """Ambil semua kategori game aktif"""
        categories = self.category_repo.get_active_categories()
        return [
            {
                "id": cat.id,
                "name": cat.name,
                "code": cat.code,
                "icon": cat.icon
            }
            for cat in categories
        ]
    
    def get_products_by_game(self, game_code: str) -> List[Dict]:
        """Ambil produk berdasarkan kode game"""
        category = self.category_repo.get_by_code(game_code)
        if not category:
            return []
        
        products = self.product_repo.get_by_category(category.id)
        return [
            {
                "id": prod.id,
                "name": prod.name,
                "code": prod.code,
                "price": prod.price,
                "stock": prod.stock,
                "description": prod.description
            }
            for prod in products if prod.stock > 0
        ]
