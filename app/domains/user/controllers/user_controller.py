from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.shared.dependencies.admin_auth_deps import get_current_admin
from app.domains.admin.models.admin import Admin
from app.shared.responses.api_response import APIResponse

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
        # Mock statistik user
        stats = {
            "total_users": 1520,
            "active_users": 1340,
            "new_users_today": 15,
            "new_users_this_week": 89,
            "new_users_this_month": 234,
            "verified_users": 1200,
            "unverified_users": 320,
            "banned_users": 12,
            "premium_users": 45
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
        # Mock data user
        all_users = []
        for i in range(1, 101):  # 100 user mock
            all_users.append({
                "id": i,
                "username": f"user{i}",
                "email": f"user{i}@example.com",
                "full_name": f"User {i}",
                "phone": f"08123456{i:03d}",
                "status": ["active", "inactive", "banned"][i % 3],
                "is_verified": i % 2 == 0,
                "balance": (i * 10000) % 500000,
                "total_transactions": i * 5,
                "last_login": (datetime.now() - timedelta(days=i % 30)).isoformat(),
                "created_at": (datetime.now() - timedelta(days=i * 2)).isoformat()
            })
        
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
        # Mock create user
        new_user = {
            "id": 999,
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
        # Mock update user
        updated_user = {
            "id": user_id,
            "username": user_data.get("username", f"user{user_id}"),
            "email": user_data.get("email", f"user{user_id}@example.com"),
            "full_name": user_data.get("full_name", f"User {user_id}"),
            "phone": user_data.get("phone", f"08123456{user_id:03d}"),
            "status": user_data.get("status", "active"),
            "is_verified": user_data.get("is_verified", False),
            "balance": user_data.get("balance", 0),
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
        # Mock delete user
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
        
        # Mock update status
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
        
        # Mock update balance
        updated_user = {
            "id": user_id,
            "balance": amount if action == "set" else 100000 + amount,
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
