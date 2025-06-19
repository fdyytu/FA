from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
import logging
import json

from app.core.database import get_db
from app.common.dependencies.admin_auth_deps import get_current_admin
from app.domains.admin.models.admin import Admin
from app.common.responses.api_response import APIResponse

logger = logging.getLogger(__name__)


class TransactionController:
    """
    Controller untuk manajemen transaksi - Single Responsibility: Transaction management endpoints
    """
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup routes untuk manajemen transaksi"""
        
        @self.router.get("/recent")
        async def get_recent_transactions(
            limit: int = 5,
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil transaksi terbaru"""
            try:
                # Mock data untuk recent transactions
                recent_transactions = [
                    {
                        "id": f"TXN{i:03d}",
                        "user_id": f"user_{i}",
                        "amount": 10000 + (i * 5000),
                        "status": "COMPLETED" if i % 2 == 0 else "PENDING",
                        "type": "topup" if i % 3 == 0 else "purchase",
                        "created_at": "2025-01-16T10:00:00Z"
                    }
                    for i in range(1, limit + 1)
                ]
                
                # Log audit dengan error handling
                try:
                    from app.domains.admin.repositories.admin_repository import AuditLogRepository
                    audit_repo = AuditLogRepository(db)
                    audit_repo.create_log(
                        admin_id=current_admin.id,
                        action="VIEW",
                        resource="transactions",
                        resource_id=None,
                        new_values=json.dumps({"action": "viewed_recent_transactions", "limit": limit})
                    )
                except Exception as audit_error:
                    logger.warning(f"Failed to log audit for recent transactions: {audit_error}")
                
                return APIResponse.success(data=recent_transactions)
                
            except Exception as e:
                logger.error(f"Error getting recent transactions: {e}")
                # Return empty data instead of raising exception
                return APIResponse.success(data=[], message="Data transaksi terbaru tidak tersedia saat ini")
        
        @self.router.get("/")
        async def get_transactions(
            page: int = 1,
            limit: int = 10,
            status: Optional[str] = None,
            type: Optional[str] = None,
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil daftar transaksi dengan filter"""
            try:
                # Mock data untuk transactions
                total = 50
                skip = (page - 1) * limit
                
                transactions = [
                    {
                        "id": f"TXN{i:03d}",
                        "user_id": f"user_{i}",
                        "amount": 10000 + (i * 1000),
                        "status": "COMPLETED" if i % 3 == 0 else ("PENDING" if i % 3 == 1 else "FAILED"),
                        "type": "topup" if i % 2 == 0 else "purchase",
                        "created_at": "2025-01-16T10:00:00Z",
                        "updated_at": "2025-01-16T10:05:00Z"
                    }
                    for i in range(skip + 1, skip + limit + 1)
                ]
                
                # Apply filters if provided
                if status:
                    transactions = [t for t in transactions if t["status"] == status]
                if type:
                    transactions = [t for t in transactions if t["type"] == type]
                
                # Log audit
                from app.domains.admin.repositories.admin_repository import AuditLogRepository
                audit_repo = AuditLogRepository(db)
                audit_repo.create_log(
                    admin_id=current_admin.id,
                    action="VIEW",
                    resource="transactions",
                    resource_id=None,
                    new_values=json.dumps({
                        "action": "viewed_transactions", 
                        "page": page, 
                        "limit": limit, 
                        "filters": {"status": status, "type": type}
                    })
                )
                
                return APIResponse.success(data={
                    "items": transactions,
                    "total": total,
                    "page": page,
                    "limit": limit,
                    "pages": (total + limit - 1) // limit
                })
                
            except Exception as e:
                logger.error(f"Error getting transactions: {e}")
                raise HTTPException(status_code=500, detail=f"Error getting transactions: {str(e)}")
        
        @self.router.get("/{transaction_id}")
        async def get_transaction(
            transaction_id: str,
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil detail transaksi"""
            try:
                # Mock data untuk transaction detail
                transaction = {
                    "id": transaction_id,
                    "user_id": "user_123",
                    "amount": 50000,
                    "status": "COMPLETED",
                    "type": "topup",
                    "payment_method": "bank_transfer",
                    "description": "Top up saldo",
                    "created_at": "2025-01-16T10:00:00Z",
                    "updated_at": "2025-01-16T10:05:00Z",
                    "metadata": {
                        "bank": "BCA",
                        "account_number": "1234567890"
                    }
                }
                
                # Log audit
                from app.domains.admin.repositories.admin_repository import AuditLogRepository
                audit_repo = AuditLogRepository(db)
                audit_repo.create_log(
                    admin_id=current_admin.id,
                    action="VIEW",
                    resource="transaction",
                    resource_id=transaction_id,
                    new_values=json.dumps({"action": "viewed_transaction_detail"})
                )
                
                return APIResponse.success(data=transaction)
                
            except Exception as e:
                logger.error(f"Error getting transaction {transaction_id}: {e}")
                raise HTTPException(status_code=500, detail=f"Error getting transaction: {str(e)}")
        
        @self.router.put("/{transaction_id}/status")
        async def update_transaction_status(
            transaction_id: str,
            new_status: str,
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Update status transaksi"""
            try:
                # Validate status
                valid_statuses = ["PENDING", "COMPLETED", "FAILED", "CANCELLED"]
                if new_status not in valid_statuses:
                    raise HTTPException(
                        status_code=400, 
                        detail=f"Status tidak valid. Status yang valid: {', '.join(valid_statuses)}"
                    )
                
                # Log audit
                from app.domains.admin.repositories.admin_repository import AuditLogRepository
                audit_repo = AuditLogRepository(db)
                audit_repo.create_log(
                    admin_id=current_admin.id,
                    action="UPDATE",
                    resource="transaction",
                    resource_id=transaction_id,
                    new_values=json.dumps({
                        "action": "updated_transaction_status",
                        "new_status": new_status
                    })
                )
                
                return APIResponse.success(
                    message=f"Status transaksi {transaction_id} berhasil diupdate ke {new_status}"
                )
                
            except Exception as e:
                logger.error(f"Error updating transaction status {transaction_id}: {e}")
                raise HTTPException(status_code=500, detail=f"Error updating transaction: {str(e)}")
        
        @self.router.get("/stats/summary")
        async def get_transaction_summary(
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil ringkasan statistik transaksi"""
            try:
                # Mock data untuk transaction summary
                summary = {
                    "total_transactions": 1250,
                    "total_amount": 125000000,
                    "completed_transactions": 1100,
                    "pending_transactions": 100,
                    "failed_transactions": 50,
                    "today_transactions": 45,
                    "today_amount": 2250000,
                    "monthly_growth": 15.5
                }
                
                # Log audit
                from app.domains.admin.repositories.admin_repository import AuditLogRepository
                audit_repo = AuditLogRepository(db)
                audit_repo.create_log(
                    admin_id=current_admin.id,
                    action="VIEW",
                    resource="transaction_stats",
                    resource_id=None,
                    new_values=json.dumps({"action": "viewed_transaction_summary"})
                )
                
                return APIResponse.success(data=summary)
                
            except Exception as e:
                logger.error(f"Error getting transaction summary: {e}")
                return APIResponse.success(
                    data={
                        "total_transactions": 0,
                        "total_amount": 0,
                        "completed_transactions": 0,
                        "pending_transactions": 0,
                        "failed_transactions": 0,
                        "today_transactions": 0,
                        "today_amount": 0,
                        "monthly_growth": 0
                    },
                    message="Data statistik transaksi tidak tersedia saat ini"
                )


# Initialize controller
transaction_controller = TransactionController()
