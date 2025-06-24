"""
Transaction Management Controller
Controller untuk manajemen transaksi (CRUD operations)
Maksimal 50 baris per file
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
import logging
import json

from app.core.database import get_db
from app.common.dependencies.admin_auth_deps import get_current_admin
from app.domains.admin.models.admin import Admin

logger = logging.getLogger(__name__)


class TransactionManagementController:
    """Controller untuk manajemen transaksi - Single Responsibility"""
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup routes untuk manajemen transaksi"""
        
        @self.router.get("/")
        async def get_transactions(
            page: int = 1, limit: int = 10, status: Optional[str] = None, type: Optional[str] = None,
            current_admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)
        ):
            """Ambil daftar transaksi dengan filter"""
            try:
                total = 0
                skip = (page - 1) * limit
                transactions = []  # Placeholder for real data
                
                # Apply filters if provided
                if status:
                    transactions = [t for t in transactions if t.get("status") == status]
                if type:
                    transactions = [t for t in transactions if t.get("type") == type]
                
                # Log audit
                self._log_audit(db, current_admin.id, "VIEW", "transactions", None, 
                              {"action": "viewed_transactions", "page": page, "limit": limit, 
                               "filters": {"status": status, "type": type}})
                
                return {"success": True, "data": {"items": transactions, "total": total, 
                       "page": page, "limit": limit, "pages": (total + limit - 1) // limit}}
                
            except Exception as e:
                logger.error(f"Error getting transactions: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail=f"Error getting transactions: {str(e)}")
    
    def _log_audit(self, db: Session, admin_id: str, action: str, resource: str, resource_id: str, data: dict):
        """Helper method untuk audit logging"""
        try:
            from app.domains.admin.repositories.admin_repository import AuditLogRepository
            audit_repo = AuditLogRepository(db)
            audit_repo.create_log(admin_id=admin_id, action=action, resource=resource, 
                                resource_id=resource_id, new_values=json.dumps(data))
        except Exception as e:
            logger.warning(f"Failed to log audit: {e}")
