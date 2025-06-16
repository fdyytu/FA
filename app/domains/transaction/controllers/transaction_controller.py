from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.shared.dependencies.admin_auth_deps import get_current_admin
from app.domains.admin.models.admin import Admin
from app.shared.responses.api_response import APIResponse

router = APIRouter()

@router.get("/recent")
async def get_recent_transactions(
    limit: int = Query(5, ge=1, le=50, description="Jumlah transaksi terbaru"),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Ambil transaksi terbaru untuk dashboard admin
    """
    try:
        # Query untuk mengambil transaksi terbaru
        # Karena model transaction belum ada, kita buat mock data dulu
        mock_transactions = [
            {
                "id": 1,
                "user_id": 101,
                "username": "user1",
                "product_name": "Pulsa Telkomsel 10K",
                "amount": 12000,
                "status": "success",
                "created_at": (datetime.now() - timedelta(minutes=5)).isoformat(),
                "transaction_type": "pulsa"
            },
            {
                "id": 2,
                "user_id": 102,
                "username": "user2", 
                "product_name": "Token PLN 20K",
                "amount": 22000,
                "status": "success",
                "created_at": (datetime.now() - timedelta(minutes=15)).isoformat(),
                "transaction_type": "pln"
            },
            {
                "id": 3,
                "user_id": 103,
                "username": "user3",
                "product_name": "Paket Data XL 1GB",
                "amount": 15000,
                "status": "pending",
                "created_at": (datetime.now() - timedelta(minutes=30)).isoformat(),
                "transaction_type": "data"
            },
            {
                "id": 4,
                "user_id": 104,
                "username": "user4",
                "product_name": "Voucher Game 50K",
                "amount": 52000,
                "status": "success",
                "created_at": (datetime.now() - timedelta(hours=1)).isoformat(),
                "transaction_type": "voucher"
            },
            {
                "id": 5,
                "user_id": 105,
                "username": "user5",
                "product_name": "Pulsa Indosat 25K",
                "amount": 27000,
                "status": "failed",
                "created_at": (datetime.now() - timedelta(hours=2)).isoformat(),
                "transaction_type": "pulsa"
            }
        ]
        
        # Batasi sesuai limit yang diminta
        recent_transactions = mock_transactions[:limit]
        
        return APIResponse.success(
            data=recent_transactions,
            message=f"Berhasil mengambil {len(recent_transactions)} transaksi terbaru"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Gagal mengambil transaksi terbaru: {str(e)}"
        )

@router.get("/")
async def get_all_transactions(
    page: int = Query(1, ge=1, description="Halaman"),
    size: int = Query(10, ge=1, le=100, description="Jumlah per halaman"),
    status: Optional[str] = Query(None, description="Filter berdasarkan status"),
    transaction_type: Optional[str] = Query(None, description="Filter berdasarkan tipe"),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Ambil semua transaksi dengan pagination dan filter
    """
    try:
        # Mock data untuk semua transaksi
        all_transactions = []
        for i in range(1, 51):  # 50 transaksi mock
            all_transactions.append({
                "id": i,
                "user_id": 100 + i,
                "username": f"user{i}",
                "product_name": f"Product {i}",
                "amount": 10000 + (i * 1000),
                "status": ["success", "pending", "failed"][i % 3],
                "created_at": (datetime.now() - timedelta(hours=i)).isoformat(),
                "transaction_type": ["pulsa", "data", "pln", "voucher"][i % 4]
            })
        
        # Filter berdasarkan status jika ada
        if status:
            all_transactions = [t for t in all_transactions if t["status"] == status]
            
        # Filter berdasarkan tipe jika ada
        if transaction_type:
            all_transactions = [t for t in all_transactions if t["transaction_type"] == transaction_type]
        
        # Pagination
        total = len(all_transactions)
        start = (page - 1) * size
        end = start + size
        transactions = all_transactions[start:end]
        
        return APIResponse.success(
            data={
                "transactions": transactions,
                "pagination": {
                    "page": page,
                    "size": size,
                    "total": total,
                    "pages": (total + size - 1) // size
                }
            },
            message=f"Berhasil mengambil {len(transactions)} transaksi"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Gagal mengambil transaksi: {str(e)}"
        )

@router.get("/stats")
async def get_transaction_stats(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Ambil statistik transaksi untuk dashboard
    """
    try:
        # Mock statistik transaksi
        stats = {
            "total_transactions": 1250,
            "successful_transactions": 1100,
            "pending_transactions": 75,
            "failed_transactions": 75,
            "total_revenue": 15750000,
            "today_transactions": 45,
            "today_revenue": 567000,
            "success_rate": 88.0,
            "popular_products": [
                {"name": "Pulsa Telkomsel", "count": 450},
                {"name": "Token PLN", "count": 320},
                {"name": "Paket Data XL", "count": 280},
                {"name": "Voucher Game", "count": 200}
            ]
        }
        
        return APIResponse.success(
            data=stats,
            message="Berhasil mengambil statistik transaksi"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Gagal mengambil statistik transaksi: {str(e)}"
        )
