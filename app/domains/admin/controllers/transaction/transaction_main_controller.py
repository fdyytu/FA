"""
Transaction Main Controller
Controller untuk operasi utama transaksi
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


class TransactionMainController:
    """Controller untuk operasi utama transaksi - Single Responsibility"""
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup routes untuk operasi utama transaksi"""
        
        @self.router.get("/recent")
        async def get_recent_transactions(
            limit: int = 5,
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil transaksi terbaru"""
            try:
                recent_transactions = []  # Placeholder for real data
                
                # Log audit dengan error handling
                try:
                    from app.domains.admin.repositories.admin_repository import AuditLogRepository
                    audit_repo = AuditLogRepository(db)
                    audit_repo.create_log(
                        admin_id=current_admin.id, action="VIEW", resource="transactions",
                        resource_id=None, new_values=json.dumps({"action": "viewed_recent_transactions", "limit": limit})
                    )
                except Exception as audit_error:
                    logger.warning(f"Failed to log audit for recent transactions: {audit_error}")
                
                logger.info(f"Retrieved {len(recent_transactions)} recent transactions for admin {current_admin.username}")
                return {"success": True, "data": recent_transactions}
                
            except Exception as e:
                logger.error(f"Error getting recent transactions: {e}", exc_info=True)
                return {"success": True, "data": [], "message": "Data transaksi terbaru tidak tersedia saat ini"}
