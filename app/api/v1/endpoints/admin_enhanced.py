from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.domains.admin.controllers.admin_controller import (
    AdminAuthController, AdminManagementController, ConfigurationController,
    UserManagementController, ProductManagementController, DashboardController,
    MarginManagementController
)
from app.services.ppob.providers.provider_factory import provider_factory
from app.shared.dependencies.auth_deps import get_current_admin, get_current_super_admin
from app.domains.admin.models.admin import Admin
from app.shared.responses.api_response import APIResponse


# Initialize controllers
auth_controller = AdminAuthController()
admin_controller = AdminManagementController()
config_controller = ConfigurationController()
user_controller = UserManagementController()
product_controller = ProductManagementController()
dashboard_controller = DashboardController()
margin_controller = MarginManagementController()

# Main admin router
router = APIRouter()

# Include all controller routes
router.include_router(
    auth_controller.router,
    prefix="/auth",
    tags=["Admin Authentication"]
)

router.include_router(
    admin_controller.router,
    prefix="/admins",
    tags=["Admin Management"]
)

router.include_router(
    config_controller.router,
    prefix="/config",
    tags=["Configuration Management"]
)

router.include_router(
    user_controller.router,
    prefix="/users",
    tags=["User Management"]
)

router.include_router(
    product_controller.router,
    prefix="/products",
    tags=["Product Management"]
)

router.include_router(
    dashboard_controller.router,
    prefix="/dashboard",
    tags=["Dashboard"]
)

router.include_router(
    margin_controller.router,
    prefix="/margins",
    tags=["Margin Management"]
)


# Provider management endpoints
@router.get("/providers/status")
async def get_provider_status(
    current_admin: Admin = Depends(get_current_admin)
):
    """Ambil status semua provider"""
    try:
        provider_stats = provider_factory.get_provider_stats()
        return APIResponse.success(data=provider_stats)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal mengambil status provider: {str(e)}"
        )


@router.post("/providers/{provider_name}/enable")
async def enable_provider(
    provider_name: str,
    current_admin: Admin = Depends(get_current_admin)
):
    """Aktifkan provider"""
    try:
        success = provider_factory.enable_provider(provider_name)
        if success:
            return APIResponse.success(message=f"Provider {provider_name} berhasil diaktifkan")
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Provider tidak ditemukan"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal mengaktifkan provider: {str(e)}"
        )


@router.post("/providers/{provider_name}/disable")
async def disable_provider(
    provider_name: str,
    current_admin: Admin = Depends(get_current_admin)
):
    """Nonaktifkan provider"""
    try:
        success = provider_factory.disable_provider(provider_name)
        if success:
            return APIResponse.success(message=f"Provider {provider_name} berhasil dinonaktifkan")
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Provider tidak ditemukan"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal menonaktifkan provider: {str(e)}"
        )


@router.post("/providers/health-check")
async def health_check_providers(
    current_admin: Admin = Depends(get_current_admin)
):
    """Lakukan health check untuk semua provider"""
    try:
        health_results = await provider_factory.health_check_all_providers()
        return APIResponse.success(data=health_results)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal melakukan health check: {str(e)}"
        )


@router.put("/providers/{provider_name}/config")
async def update_provider_config(
    provider_name: str,
    config: dict,
    current_admin: Admin = Depends(get_current_super_admin)
):
    """Update konfigurasi provider"""
    try:
        success = provider_factory.update_provider_config(provider_name, config)
        if success:
            return APIResponse.success(message=f"Konfigurasi provider {provider_name} berhasil diupdate")
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Provider tidak ditemukan"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal mengupdate konfigurasi provider: {str(e)}"
        )


# System monitoring endpoints
@router.get("/system/health")
async def system_health_check(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Health check sistem secara keseluruhan"""
    try:
        # Check database
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    # Check providers
    try:
        provider_stats = provider_factory.get_provider_stats()
        active_providers = len([
            p for p in provider_stats.values() 
            if p["is_active"] and p["status"] == "healthy"
        ])
        provider_status = "healthy" if active_providers > 0 else "unhealthy"
    except Exception as e:
        provider_status = f"unhealthy: {str(e)}"
    
    overall_status = "healthy" if all([
        db_status == "healthy",
        provider_status == "healthy"
    ]) else "unhealthy"
    
    return APIResponse.success(data={
        "overall_status": overall_status,
        "components": {
            "database": db_status,
            "providers": provider_status,
            "active_providers": active_providers if 'active_providers' in locals() else 0
        }
    })


@router.get("/system/stats")
async def get_system_stats(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Ambil statistik sistem"""
    try:
        from app.domains.admin.repositories.admin_repository import DashboardRepository
        dashboard_repo = DashboardRepository(db)
        
        # Get basic stats
        stats = dashboard_repo.get_dashboard_stats()
        
        # Get provider stats
        provider_stats = provider_factory.get_provider_stats()
        
        # Get recent activity
        recent_transactions = dashboard_repo.get_recent_transactions(5)
        
        return APIResponse.success(data={
            "system_stats": stats,
            "provider_stats": provider_stats,
            "recent_activity": [
                {
                    "id": tx.id,
                    "type": "transaction",
                    "description": f"{tx.product_name} - {tx.customer_number}",
                    "amount": float(tx.total_amount),
                    "status": tx.status.value if tx.status else "unknown",
                    "timestamp": tx.created_at.isoformat()
                }
                for tx in recent_transactions
            ]
        })
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal mengambil statistik sistem: {str(e)}"
        )


# Audit log endpoints
@router.get("/audit-logs")
async def get_audit_logs(
    page: int = 1,
    size: int = 10,
    admin_id: Optional[str] = None,
    action: Optional[str] = None,
    resource: Optional[str] = None,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Ambil audit logs dengan filter"""
    try:
        from app.domains.admin.repositories.admin_repository import AuditLogRepository
        audit_repo = AuditLogRepository(db)
        
        skip = (page - 1) * size
        logs, total = audit_repo.get_logs_with_pagination(
            skip, size, admin_id, action, resource
        )
        
        from app.domains.admin.schemas.admin_schemas import PaginatedResponse, AuditLogResponse
        
        return PaginatedResponse(
            items=[AuditLogResponse.from_orm(log) for log in logs],
            total=total,
            page=page,
            size=size,
            pages=(total + size - 1) // size
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal mengambil audit logs: {str(e)}"
        )


# Backup and maintenance endpoints
@router.post("/maintenance/backup")
async def create_backup(
    current_admin: Admin = Depends(get_current_super_admin)
):
    """Buat backup database"""
    try:
        # Implementasi backup sederhana
        # Bisa diperluas dengan backup ke cloud storage
        import subprocess
        import datetime
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"backup_{timestamp}.sql"
        
        # Note: Ini contoh sederhana, sesuaikan dengan database yang digunakan
        result = subprocess.run([
            "sqlite3", "fa_database.db", f".backup {backup_file}"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            return APIResponse.success(
                message="Backup berhasil dibuat",
                data={"backup_file": backup_file}
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Gagal membuat backup"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal membuat backup: {str(e)}"
        )


@router.post("/maintenance/cleanup")
async def cleanup_old_data(
    days: int = 30,
    current_admin: Admin = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Bersihkan data lama"""
    try:
        from datetime import datetime, timedelta
        from app.domains.admin.models.admin import AdminAuditLog
        
        # Hapus audit log yang lebih dari X hari
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        deleted_count = db.query(AdminAuditLog).filter(
            AdminAuditLog.created_at < cutoff_date
        ).delete()
        
        db.commit()
        
        return APIResponse.success(
            message=f"Berhasil menghapus {deleted_count} record audit log lama",
            data={"deleted_count": deleted_count}
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal membersihkan data: {str(e)}"
        )
