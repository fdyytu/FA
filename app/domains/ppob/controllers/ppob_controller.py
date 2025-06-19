from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.shared.responses.api_response import APIResponse

router = APIRouter()

@router.get("/categories")
async def get_categories(db: Session = Depends(get_db)):
    """Get available PPOB categories"""
    try:
        # Return simple category list
        categories = [
            {"id": 1, "name": "PLN", "code": "PLN", "description": "Listrik PLN"},
            {"id": 2, "name": "PDAM", "code": "PDAM", "description": "Air PDAM"},
            {"id": 3, "name": "Telkom", "code": "TELKOM", "description": "Telepon Telkom"},
            {"id": 4, "name": "Internet", "code": "INTERNET", "description": "Internet"},
            {"id": 5, "name": "TV Cable", "code": "TV", "description": "TV Kabel"}
        ]
        
        return APIResponse.success(
            data=categories,
            message="Kategori PPOB berhasil diambil"
        )
    except Exception as e:
        return APIResponse.error(f"Gagal mengambil kategori: {str(e)}")

@router.get("/products/{category_id}")
async def get_products_by_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    """Get products by category"""
    try:
        # Return simple product list based on category
        products = [
            {
                "id": 1,
                "product_code": f"PROD_{category_id}_001",
                "product_name": f"Product Category {category_id}",
                "category_id": category_id,
                "price": 10000,
                "admin_fee": 1000,
                "is_active": True
            }
        ]
        
        return APIResponse.success(
            data=products,
            message=f"Produk kategori {category_id} berhasil diambil"
        )
    except Exception as e:
        return APIResponse.error(f"Gagal mengambil produk: {str(e)}")

@router.get("/transactions")
async def get_user_transactions(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100)
):
    """Get user transactions"""
    try:
        # Return empty transaction list for now
        return APIResponse.success(
            data={
                "transactions": [],
                "total": 0,
                "page": page,
                "per_page": per_page,
                "total_pages": 0
            },
            message="Transaksi berhasil diambil"
        )
    except Exception as e:
        return APIResponse.error(f"Gagal mengambil transaksi: {str(e)}")

@router.get("/stats")
async def get_transaction_stats(db: Session = Depends(get_db)):
    """Get transaction statistics"""
    try:
        stats = {
            "total_transactions": 0,
            "success_transactions": 0,
            "failed_transactions": 0,
            "pending_transactions": 0,
            "total_amount": 0.0,
            "today_transactions": 0,
            "success_rate": 0.0
        }
        
        return APIResponse.success(
            data=stats,
            message="Statistik berhasil diambil"
        )
    except Exception as e:
        return APIResponse.error(f"Gagal mengambil statistik: {str(e)}")
