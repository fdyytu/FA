from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging
import time
from typing import List

from app.core.database import get_db
from app.domains.admin.services.admin_management_service import AdminManagementService
from app.domains.admin.schemas.admin_schemas import AdminResponse
from app.common.dependencies.admin_auth_deps import get_current_admin, get_current_super_admin
from app.domains.admin.models.admin import Admin

# Setup enhanced logging
logger = logging.getLogger(__name__)


class AdminAuthController:
    """
    Controller untuk authentication dan authorization admin
    Single Responsibility: Menangani validasi akses dan permissions
    """
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
        logger.info("AdminAuthController initialized")
    
    def _setup_routes(self):
        """Setup routes untuk auth dan permissions dengan enhanced logging"""
        
        @self.router.get("/permissions")
        async def get_admin_permissions(
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil permissions admin saat ini"""
            start_time = time.time()
            request_id = f"get_permissions_{int(start_time)}"
            
            logger.info(f"[{request_id}] Request get_admin_permissions - admin_id: {current_admin.id}")
            
            try:
                admin_service = AdminManagementService(db)
                
                logger.debug(f"[{request_id}] Fetching permissions for admin: {current_admin.id}")
                
                # Implementasi sederhana untuk permissions
                # Bisa diperluas sesuai sistem role-based access control
                permissions = {
                    "admin_id": current_admin.id,
                    "username": current_admin.username,
                    "role": getattr(current_admin, 'role', 'admin'),
                    "is_super_admin": getattr(current_admin, 'is_super_admin', False),
                    "permissions": [
                        "read_admins",
                        "read_audit_logs",
                        "manage_products" if getattr(current_admin, 'is_super_admin', False) else None,
                        "manage_admins" if getattr(current_admin, 'is_super_admin', False) else None
                    ]
                }
                
                # Filter None values
                permissions["permissions"] = [p for p in permissions["permissions"] if p is not None]
                
                duration = time.time() - start_time
                logger.info(f"[{request_id}] Successfully retrieved permissions for admin {current_admin.id} in {duration:.3f}s")
                
                # Log akses permissions untuk audit
                logger.warning(f"[AUTH_ACCESS] Permissions accessed - admin_id: {current_admin.id}, "
                             f"permissions_count: {len(permissions['permissions'])}")
                
                return permissions
                
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"[{request_id}] Error getting permissions after {duration:.3f}s: {str(e)}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Gagal mengambil permissions"
                )
        
        @self.router.get("/profile", response_model=AdminResponse)
        async def get_admin_profile(
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil profile admin saat ini"""
            start_time = time.time()
            request_id = f"get_profile_{int(start_time)}"
            
            logger.info(f"[{request_id}] Request get_admin_profile - admin_id: {current_admin.id}")
            
            try:
                admin_service = AdminManagementService(db)
                
                logger.debug(f"[{request_id}] Fetching profile for admin: {current_admin.id}")
                
                # Ambil data admin terbaru dari database
                admin = admin_service.get_admin_by_id(current_admin.id)
                
                if not admin:
                    logger.warning(f"[{request_id}] Admin profile not found - admin_id: {current_admin.id}")
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Profile admin tidak ditemukan"
                    )
                
                duration = time.time() - start_time
                logger.info(f"[{request_id}] Successfully retrieved profile for admin {current_admin.id} in {duration:.3f}s")
                
                # Log akses profile untuk audit
                logger.info(f"[AUTH_ACCESS] Profile accessed - admin_id: {current_admin.id}")
                
                return AdminResponse.from_orm(admin)
                
            except HTTPException:
                raise
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"[{request_id}] Error getting profile after {duration:.3f}s: {str(e)}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Gagal mengambil profile admin"
                )
        
        @self.router.post("/validate-access")
        async def validate_admin_access(
            resource: str,
            action: str,
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Validasi akses admin untuk resource dan action tertentu"""
            start_time = time.time()
            request_id = f"validate_access_{int(start_time)}"
            
            logger.info(f"[{request_id}] Request validate_admin_access - admin_id: {current_admin.id}, "
                       f"resource: {resource}, action: {action}")
            
            try:
                admin_service = AdminManagementService(db)
                
                logger.debug(f"[{request_id}] Validating access for admin {current_admin.id} "
                           f"to {action} on {resource}")
                
                # Implementasi sederhana untuk validasi akses
                # Bisa diperluas dengan sistem RBAC yang lebih kompleks
                is_super_admin = getattr(current_admin, 'is_super_admin', False)
                
                # Definisi aturan akses sederhana
                access_rules = {
                    "admin": {
                        "read": True,
                        "create": is_super_admin,
                        "update": is_super_admin,
                        "delete": is_super_admin
                    },
                    "product": {
                        "read": True,
                        "create": is_super_admin,
                        "update": is_super_admin,
                        "delete": is_super_admin
                    },
                    "audit_log": {
                        "read": True,
                        "export": is_super_admin
                    }
                }
                
                # Validasi akses
                has_access = False
                if resource in access_rules:
                    has_access = access_rules[resource].get(action, False)
                
                validation_result = {
                    "admin_id": current_admin.id,
                    "resource": resource,
                    "action": action,
                    "has_access": has_access,
                    "is_super_admin": is_super_admin
                }
                
                duration = time.time() - start_time
                logger.info(f"[{request_id}] Access validation completed for admin {current_admin.id} in {duration:.3f}s - "
                           f"access_granted: {has_access}")
                
                # Log validasi akses untuk audit (penting untuk keamanan)
                log_level = logger.warning if has_access else logger.error
                log_level(f"[ACCESS_VALIDATION] Access validation - admin_id: {current_admin.id}, "
                         f"resource: {resource}, action: {action}, granted: {has_access}")
                
                return validation_result
                
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"[{request_id}] Error validating access after {duration:.3f}s: {str(e)}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Gagal memvalidasi akses"
                )
        
        @self.router.get("/session-info")
        async def get_session_info(
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil informasi session admin saat ini"""
            start_time = time.time()
            request_id = f"get_session_info_{int(start_time)}"
            
            logger.info(f"[{request_id}] Request get_session_info - admin_id: {current_admin.id}")
            
            try:
                logger.debug(f"[{request_id}] Fetching session info for admin: {current_admin.id}")
                
                # Implementasi sederhana untuk session info
                session_info = {
                    "admin_id": current_admin.id,
                    "username": current_admin.username,
                    "session_start": getattr(current_admin, 'last_login', None),
                    "is_active": True,
                    "permissions_count": 4 if getattr(current_admin, 'is_super_admin', False) else 2
                }
                
                duration = time.time() - start_time
                logger.info(f"[{request_id}] Successfully retrieved session info for admin {current_admin.id} in {duration:.3f}s")
                
                # Log akses session info
                logger.info(f"[AUTH_ACCESS] Session info accessed - admin_id: {current_admin.id}")
                
                return session_info
                
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"[{request_id}] Error getting session info after {duration:.3f}s: {str(e)}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Gagal mengambil informasi session"
                )
