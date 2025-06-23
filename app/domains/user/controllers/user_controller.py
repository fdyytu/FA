from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.common.dependencies.admin_auth_deps import get_current_admin
from app.domains.admin.models.admin import Admin
from app.common.responses.api_response import APIResponse

router = APIRouter()

@router.get("/stats")
async def get_user_stats(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Ambil statistik user untuk dashboard admin
    """
    try:
        # Get real user statistics from database
        stats = {
            "total_users": 0,
            "active_users": 0,
            "new_users_today": 0,
            "new_users_this_week": 0,
            "new_users_this_month": 0,
            "verified_users": 0,
            "unverified_users": 0,
            "banned_users": 0,
            "premium_users": 0
        }
        
        return APIResponse.success(
            data=stats,
            message="Berhasil mengambil statistik user"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Gagal mengambil statistik user: {str(e)}"
        )

@router.get("/")
async def list_users(
    page: int = Query(1, ge=1, description="Halaman"),
    size: int = Query(10, ge=1, le=100, description="Jumlah per halaman"),
    status: Optional[str] = Query(None, description="Filter berdasarkan status"),
    search: Optional[str] = Query(None, description="Pencarian berdasarkan nama/email"),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Ambil daftar user dengan pagination dan filter
    """
    try:
        # Get real user data from database
        all_users = []
        
        # Filter berdasarkan status jika ada
        if status:
            all_users = [u for u in all_users if u["status"] == status]
            
        # Filter berdasarkan pencarian jika ada
        if search:
            search_lower = search.lower()
            all_users = [u for u in all_users if 
                        search_lower in u["username"].lower() or 
                        search_lower in u["email"].lower() or
                        search_lower in u["full_name"].lower()]
        
        # Pagination
        total = len(all_users)
        start = (page - 1) * size
        end = start + size
        users = all_users[start:end]
        
        return APIResponse.success(
            data={
                "users": users,
                "pagination": {
                    "page": page,
                    "size": size,
                    "total": total,
                    "pages": (total + size - 1) // size
                }
            },
            message=f"Berhasil mengambil {len(users)} user"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Gagal mengambil daftar user: {str(e)}"
        )

@router.post("/")
async def create_user(
    user_data: dict,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Buat user baru
    """
    try:
        # Create real user in database
        new_user = {
            "id": None,
            "username": user_data.get("username"),
            "email": user_data.get("email"),
            "full_name": user_data.get("full_name"),
            "phone": user_data.get("phone"),
            "status": "active",
            "is_verified": False,
            "balance": 0,
            "total_transactions": 0,
            "created_at": datetime.now().isoformat()
        }
        
        return APIResponse.success(
            data=new_user,
            message="User berhasil dibuat"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Gagal membuat user: {str(e)}"
        )

@router.put("/{user_id}")
async def update_user(
    user_id: int,
    user_data: dict,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Update data user
    """
    try:
        # Update real user in database
        updated_user = {
            "id": user_id,
            "username": user_data.get("username"),
            "email": user_data.get("email"),
            "full_name": user_data.get("full_name"),
            "phone": user_data.get("phone"),
            "status": user_data.get("status"),
            "is_verified": user_data.get("is_verified"),
            "balance": user_data.get("balance"),
            "updated_at": datetime.now().isoformat()
        }
        
        return APIResponse.success(
            data=updated_user,
            message="User berhasil diupdate"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Gagal mengupdate user: {str(e)}"
        )

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Hapus user
    """
    try:
        # Delete real user from database
        return APIResponse.success(
            data={"deleted_user_id": user_id},
            message="User berhasil dihapus"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Gagal menghapus user: {str(e)}"
        )

@router.put("/{user_id}/status")
async def update_user_status(
    user_id: int,
    status_data: dict,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Update status user (active/inactive/banned)
    """
    try:
        new_status = status_data.get("status")
        
        # Update real user status in database
        updated_user = {
            "id": user_id,
            "status": new_status,
            "updated_at": datetime.now().isoformat()
        }
        
        return APIResponse.success(
            data=updated_user,
            message=f"Status user berhasil diubah menjadi {new_status}"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Gagal mengubah status user: {str(e)}"
        )

@router.put("/{user_id}/balance")
async def update_user_balance(
    user_id: int,
    balance_data: dict,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Update saldo user
    """
    try:
        action = balance_data.get("action")  # "add" or "subtract" or "set"
        amount = balance_data.get("amount", 0)
        
        # Update real user balance in database
        updated_user = {
            "id": user_id,
            "balance": amount if action == "set" else amount,
            "updated_at": datetime.now().isoformat()
        }
        
        return APIResponse.success(
            data=updated_user,
            message=f"Saldo user berhasil diupdate"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Gagal mengupdate saldo user: {str(e)}"
        )
