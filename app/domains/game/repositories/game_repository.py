"""
Repository untuk domain game
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.domains.game.models.game_models import GameCategory, GameProduct, GameValidation
from app.domains.game.schemas.game_schemas import GameCategoryCreate, GameProductCreate

class GameCategoryRepository:
    """Repository untuk kategori game"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[GameCategory]:
        return self.db.query(GameCategory).offset(skip).limit(limit).all()
    
    def get_by_id(self, category_id: int) -> Optional[GameCategory]:
        return self.db.query(GameCategory).filter(GameCategory.id == category_id).first()
    
    def get_by_code(self, code: str) -> Optional[GameCategory]:
        return self.db.query(GameCategory).filter(GameCategory.code == code).first()
    
    def create(self, category_data: GameCategoryCreate) -> GameCategory:
        db_category = GameCategory(**category_data.dict())
        self.db.add(db_category)
        self.db.commit()
        self.db.refresh(db_category)
        return db_category
    
    def get_active_categories(self) -> List[GameCategory]:
        return self.db.query(GameCategory).filter(GameCategory.is_active == True).all()

class GameProductRepository:
    """Repository untuk produk game"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[GameProduct]:
        return self.db.query(GameProduct).offset(skip).limit(limit).all()
    
    def get_by_id(self, product_id: int) -> Optional[GameProduct]:
        return self.db.query(GameProduct).filter(GameProduct.id == product_id).first()
    
    def get_by_code(self, code: str) -> Optional[GameProduct]:
        return self.db.query(GameProduct).filter(GameProduct.code == code).first()
    
    def get_by_category(self, category_id: int) -> List[GameProduct]:
        return self.db.query(GameProduct).filter(
            and_(GameProduct.category_id == category_id, GameProduct.is_active == True)
        ).all()
    
    def create(self, product_data: GameProductCreate) -> GameProduct:
        db_product = GameProduct(**product_data.dict())
        self.db.add(db_product)
        self.db.commit()
        self.db.refresh(db_product)
        return db_product
    
    def update_stock(self, product_id: int, new_stock: int) -> bool:
        product = self.get_by_id(product_id)
        if product:
            product.stock = new_stock
            self.db.commit()
            return True
        return False
