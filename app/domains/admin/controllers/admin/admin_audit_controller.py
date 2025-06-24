from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
import logging
import time

from app.core.database import get_db
from app.domains.admin.services.admin_management_service import AdminManagementService
from app.domains.admin.schemas.admin_schemas import PaginatedResponse, AuditLogResponse
from app.common.dependencies.admin_auth_deps import get_current_admin
from app.domains.admin.models.admin import Admin

# Setup enhanced logging
logger = logging.getLogger(__name__)


class AdminAuditController:
    """
    Controller untuk audit logs admin
    Single Responsibility: Menangani audit trail dan logging
    """
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
        logger.info("AdminAuditController initialized")
    
    def _setup_routes(self):
        """Setup routes untuk audit logs dengan enhanced logging"""
        
        @self.router.get("/audit-logs/", response_model=PaginatedResponse)
        async def get_audit_logs(
            page: int = 1,
            size: int = 10,
            action: Optional[str] = None,
            resource: Optional[str] = None,
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil audit logs dengan filtering dan logging akses"""
            start_time = time.time()
            request_id = f"get_audit_logs_{int(start_time)}"
            
            # Log akses ke audit logs (penting untuk keamanan)
            logger.info(f"[{request_id}] Request get_audit_logs - page: {page}, size: {size}, "
                       f"action: {action}, resource: {resource}, requested_by: {current_admin.id}")
            
            try:
                admin_service = AdminManagementService(db)
                skip = (page - 1) * size
                
                # Log query parameters untuk debugging
                logger.debug(f"[{request_id}] Fetching audit logs with skip: {skip}, limit: {size}, "
                           f"filters - action: {action}, resource: {resource}")
                
                logs, total = admin_service.get_audit_logs(skip, size, action, resource)
                
                response = PaginatedResponse(
                    items=[AuditLogResponse.from_orm(log) for log in logs],
                    total=total,
                    page=page,
                    size=size,
                    pages=(total + size - 1) // size
                )
                
                duration = time.time() - start_time
                logger.info(f"[{request_id}] Successfully retrieved {len(logs)} audit logs in {duration:.3f}s")
                
                # Log untuk audit trail akses
                logger.warning(f"[AUDIT_ACCESS] Audit logs accessed - admin_id: {current_admin.id}, "
                             f"filters: action={action}, resource={resource}, results: {len(logs)}")
                
                return response
                
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"[{request_id}] Error getting audit logs after {duration:.3f}s: {str(e)}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Gagal mengambil audit logs"
                )
        
        @self.router.get("/audit-logs/stats")
        async def get_audit_stats(
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil statistik audit logs"""
            start_time = time.time()
            request_id = f"get_audit_stats_{int(start_time)}"
            
            logger.info(f"[{request_id}] Request get_audit_stats - requested_by: {current_admin.id}")
            
            try:
                admin_service = AdminManagementService(db)
                
                # Implementasi sederhana untuk statistik audit
                # Bisa diperluas sesuai kebutuhan
                logger.debug(f"[{request_id}] Calculating audit statistics")
                
                # Placeholder untuk statistik - bisa diimplementasi di service layer
                stats = {
                    "total_logs": 0,
                    "recent_actions": [],
                    "top_resources": [],
                    "admin_activity": []
                }
                
                duration = time.time() - start_time
                logger.info(f"[{request_id}] Successfully calculated audit stats in {duration:.3f}s")
                
                # Log akses ke statistik audit
                logger.warning(f"[AUDIT_ACCESS] Audit statistics accessed - admin_id: {current_admin.id}")
                
                return stats
                
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"[{request_id}] Error getting audit stats after {duration:.3f}s: {str(e)}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Gagal mengambil statistik audit"
                )
        
        @self.router.get("/audit-logs/export")
        async def export_audit_logs(
            format: str = "csv",
            action: Optional[str] = None,
            resource: Optional[str] = None,
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Export audit logs ke file"""
            start_time = time.time()
            request_id = f"export_audit_logs_{int(start_time)}"
            
            logger.info(f"[{request_id}] Request export_audit_logs - format: {format}, "
                       f"action: {action}, resource: {resource}, requested_by: {current_admin.id}")
            
            try:
                # Validasi format
                if format not in ["csv", "json", "xlsx"]:
                    logger.warning(f"[{request_id}] Invalid export format requested: {format}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Format export tidak valid. Gunakan: csv, json, atau xlsx"
                    )
                
                admin_service = AdminManagementService(db)
                
                logger.debug(f"[{request_id}] Exporting audit logs in {format} format")
                
                # Placeholder untuk export functionality
                # Implementasi sebenarnya akan ada di service layer
                export_result = {
                    "message": f"Export audit logs dalam format {format} sedang diproses",
                    "format": format,
                    "filters": {
                        "action": action,
                        "resource": resource
                    }
                }
                
                duration = time.time() - start_time
                logger.info(f"[{request_id}] Successfully initiated audit logs export in {duration:.3f}s")
                
                # Log critical untuk export audit (keamanan tinggi)
                logger.critical(f"[AUDIT_EXPORT] Audit logs exported - admin_id: {current_admin.id}, "
                              f"format: {format}, filters: action={action}, resource={resource}")
                
                return export_result
                
            except HTTPException:
                raise
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"[{request_id}] Error exporting audit logs after {duration:.3f}s: {str(e)}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Gagal mengexport audit logs"
                )
