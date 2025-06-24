"""
Transaction Stats Controller
Controller untuk statistik transaksi
Maksimal 50 baris per file
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging
import json

from app.core.database import get_db
from app.common.dependencies.admin_auth_deps import get_current_admin
from app.domains.admin.models.admin import Admin

logger = logging.getLogger(__name__)


class TransactionStatsController:
    """Controller untuk statistik transaksi - Single Responsibility"""
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup routes untuk statistik transaksi"""
        
        @self.router.get("/stats/summary")
        async def get_transaction_summary(
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil ringkasan statistik transaksi"""
            try:
                summary = {
                    "total_transactions": 0, "total_amount": 0, "completed_transactions": 0,
                    "pending_transactions": 0, "failed_transactions": 0, "today_transactions": 0,
                    "today_amount": 0, "monthly_growth": 0
                }
                
                # Log audit
                try:
                    from app.domains.admin.repositories.admin_repository import AuditLogRepository
                    audit_repo = AuditLogRepository(db)
                    audit_repo.create_log(
                        admin_id=current_admin.id, action="VIEW", resource="transaction_stats",
                        resource_id=None, new_values=json.dumps({"action": "viewed_transaction_summary"})
                    )
                except Exception as audit_error:
                    logger.warning(f"Failed to log audit for transaction summary: {audit_error}")
                
                logger.info(f"Transaction summary retrieved for admin {current_admin.username}")
                return {"success": True, "data": summary}
                
            except Exception as e:
                logger.error(f"Error getting transaction summary: {e}", exc_info=True)
                return {"success": True, "data": summary, "message": "Data statistik transaksi tidak tersedia saat ini"}
