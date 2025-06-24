from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging
import time
from typing import List

from app.core.database import get_db
from app.domains.admin.services.admin_management_service import AdminManagementService
from app.domains.admin.schemas.admin_schemas import (
    AdminCreate, AdminUpdate, AdminResponse, PaginatedResponse
)
from app.common.dependencies.admin_auth_deps import get_current_super_admin
from app.domains.admin.models.admin import Admin

# Setup enhanced logging
logger = logging.getLogger(__name__)


class AdminCrudController:
    """
    Controller untuk operasi CRUD admin
    Single Responsibility: Menangani Create, Read, Update, Delete admin
    """
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
        logger.info("AdminCrudController initialized")
    
    def _setup_routes(self):
        """Setup routes untuk CRUD admin dengan enhanced logging"""
        
        @self.router.get("/", response_model=PaginatedResponse)
        async def get_admins(
            page: int = 1,
            size: int = 10,
            current_admin: Admin = Depends(get_current_super_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil daftar admin dengan pagination dan logging"""
            start_time = time.time()
            request_id = f"get_admins_{int(start_time)}"
            
            logger.info(f"[{request_id}] Request get_admins - page: {page}, size: {size}, admin_id: {current_admin.id}")
            
            try:
                admin_service = AdminManagementService(db)
                skip = (page - 1) * size
                
                logger.debug(f"[{request_id}] Fetching admins with skip: {skip}, limit: {size}")
                admins, total = admin_service.get_admins(skip, size)
                
                response = PaginatedResponse(
                    items=[AdminResponse.from_orm(admin) for admin in admins],
                    total=total,
                    page=page,
                    size=size,
                    pages=(total + size - 1) // size
                )
                
                duration = time.time() - start_time
                logger.info(f"[{request_id}] Successfully retrieved {len(admins)} admins in {duration:.3f}s")
                
                return response
                
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"[{request_id}] Error getting admins after {duration:.3f}s: {str(e)}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Gagal mengambil daftar admin"
                )
        
        @self.router.post("/", response_model=AdminResponse)
        async def create_admin(
            admin_data: AdminCreate,
            current_admin: Admin = Depends(get_current_super_admin),
            db: Session = Depends(get_db)
        ):
            """Buat admin baru dengan logging keamanan"""
            start_time = time.time()
            request_id = f"create_admin_{int(start_time)}"
            
            logger.info(f"[{request_id}] Request create_admin - username: {admin_data.username}, created_by: {current_admin.id}")
            
            try:
                admin_service = AdminManagementService(db)
                
                logger.debug(f"[{request_id}] Creating admin with data: {admin_data.dict(exclude={'password'})}")
                admin = admin_service.create_admin(admin_data, current_admin.id)
                
                duration = time.time() - start_time
                logger.info(f"[{request_id}] Successfully created admin {admin.id} in {duration:.3f}s")
                logger.warning(f"[SECURITY] Admin created - new_admin_id: {admin.id}, created_by: {current_admin.id}")
                
                return AdminResponse.from_orm(admin)
                
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"[{request_id}] Error creating admin after {duration:.3f}s: {str(e)}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Gagal membuat admin baru"
                )
        
        @self.router.get("/{admin_id}", response_model=AdminResponse)
        async def get_admin(
            admin_id: str,
            current_admin: Admin = Depends(get_current_super_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil detail admin dengan logging akses"""
            start_time = time.time()
            request_id = f"get_admin_{int(start_time)}"
            
            logger.info(f"[{request_id}] Request get_admin - target_admin_id: {admin_id}, requested_by: {current_admin.id}")
            
            try:
                admin_service = AdminManagementService(db)
                
                logger.debug(f"[{request_id}] Fetching admin details for ID: {admin_id}")
                admin = admin_service.get_admin_by_id(admin_id)
                
                if not admin:
                    logger.warning(f"[{request_id}] Admin not found - admin_id: {admin_id}")
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Admin tidak ditemukan"
                    )
                
                duration = time.time() - start_time
                logger.info(f"[{request_id}] Successfully retrieved admin {admin_id} in {duration:.3f}s")
                
                return AdminResponse.from_orm(admin)
                
            except HTTPException:
                raise
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"[{request_id}] Error getting admin after {duration:.3f}s: {str(e)}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Gagal mengambil detail admin"
                )
        
        @self.router.put("/{admin_id}", response_model=AdminResponse)
        async def update_admin(
            admin_id: str,
            admin_data: AdminUpdate,
            current_admin: Admin = Depends(get_current_super_admin),
            db: Session = Depends(get_db)
        ):
            """Update admin dengan logging perubahan"""
            start_time = time.time()
            request_id = f"update_admin_{int(start_time)}"
            
            logger.info(f"[{request_id}] Request update_admin - target_admin_id: {admin_id}, updated_by: {current_admin.id}")
            
            try:
                admin_service = AdminManagementService(db)
                
                # Log perubahan yang akan dilakukan (tanpa password)
                update_data = admin_data.dict(exclude_unset=True, exclude={'password'})
                logger.debug(f"[{request_id}] Updating admin with data: {update_data}")
                
                admin = admin_service.update_admin(admin_id, admin_data, current_admin.id)
                
                duration = time.time() - start_time
                logger.info(f"[{request_id}] Successfully updated admin {admin_id} in {duration:.3f}s")
                logger.warning(f"[SECURITY] Admin updated - admin_id: {admin_id}, updated_by: {current_admin.id}, changes: {list(update_data.keys())}")
                
                return AdminResponse.from_orm(admin)
                
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"[{request_id}] Error updating admin after {duration:.3f}s: {str(e)}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Gagal mengupdate admin"
                )
        
        @self.router.delete("/{admin_id}")
        async def delete_admin(
            admin_id: str,
            current_admin: Admin = Depends(get_current_super_admin),
            db: Session = Depends(get_db)
        ):
            """Hapus admin dengan logging keamanan"""
            start_time = time.time()
            request_id = f"delete_admin_{int(start_time)}"
            
            logger.info(f"[{request_id}] Request delete_admin - target_admin_id: {admin_id}, deleted_by: {current_admin.id}")
            
            try:
                admin_service = AdminManagementService(db)
                
                logger.debug(f"[{request_id}] Attempting to delete admin: {admin_id}")
                success = admin_service.delete_admin(admin_id, current_admin.id)
                
                if not success:
                    logger.warning(f"[{request_id}] Admin not found for deletion - admin_id: {admin_id}")
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Admin tidak ditemukan"
                    )
                
                duration = time.time() - start_time
                logger.info(f"[{request_id}] Successfully deleted admin {admin_id} in {duration:.3f}s")
                logger.critical(f"[SECURITY] Admin deleted - admin_id: {admin_id}, deleted_by: {current_admin.id}")
                
                return {"message": "Admin berhasil dihapus"}
                
            except HTTPException:
                raise
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"[{request_id}] Error deleting admin after {duration:.3f}s: {str(e)}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Gagal menghapus admin"
                )
