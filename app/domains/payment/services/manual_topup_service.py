"""
Manual Top Up Service - Mengikuti prinsip Single Responsibility
Hanya menangani logic manual top up
"""
from typing import Dict, Any
from decimal import Decimal
from datetime import datetime
import uuid
from sqlalchemy.orm import Session

from app.models.wallet import TopUpRequest, TopUpStatus, PaymentMethod
from app.models.user import User
from app.utils.exceptions import NotFoundError, ValidationError


class ManualTopUpService:
    """Service khusus untuk manual top up - mengikuti SRP"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def _generate_request_code(self, prefix: str = "TOPUP") -> str:
        """Generate unique request code - mengikuti DRY"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_id = str(uuid.uuid4())[:8].upper()
        return f"{prefix}-{timestamp}-{unique_id}"
    
    def create_topup_request(
        self,
        user_id: int,
        amount: Decimal,
        payment_method: PaymentMethod,
        bank_name: str = None,
        account_number: str = None,
        account_name: str = None,
        notes: str = None
    ) -> TopUpRequest:
        """Create manual top up request"""
        
        # Validasi user exists
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundError("User tidak ditemukan")
        
        # Validasi amount
        if amount <= 0:
            raise ValidationError("Amount harus lebih besar dari 0")
        
        # Create request
        request = TopUpRequest(
            user_id=user_id,
            request_code=self._generate_request_code(),
            amount=amount,
            payment_method=payment_method,
            bank_name=bank_name,
            account_number=account_number,
            account_name=account_name,
            notes=notes,
            status=TopUpStatus.PENDING,
            created_at=datetime.utcnow()
        )
        
        self.db.add(request)
        self.db.commit()
        self.db.refresh(request)
        
        return request
    
    def get_topup_request(self, request_id: int) -> TopUpRequest:
        """Get top up request by ID"""
        request = self.db.query(TopUpRequest).filter(
            TopUpRequest.id == request_id
        ).first()
        
        if not request:
            raise NotFoundError("Top up request tidak ditemukan")
        
        return request
    
    def get_user_topup_requests(
        self, 
        user_id: int, 
        status: TopUpStatus = None,
        limit: int = 10,
        offset: int = 0
    ) -> list[TopUpRequest]:
        """Get user's top up requests"""
        query = self.db.query(TopUpRequest).filter(
            TopUpRequest.user_id == user_id
        )
        
        if status:
            query = query.filter(TopUpRequest.status == status)
        
        return query.order_by(TopUpRequest.created_at.desc()).offset(offset).limit(limit).all()
    
    def approve_topup_request(
        self,
        request_id: int,
        admin_user_id: int,
        admin_notes: str = None
    ) -> TopUpRequest:
        """Approve manual top up request"""
        
        request = self.get_topup_request(request_id)
        
        if request.status != TopUpStatus.PENDING:
            raise ValidationError("Request sudah diproses sebelumnya")
        
        request.status = TopUpStatus.APPROVED
        request.admin_notes = admin_notes
        request.processed_by = admin_user_id
        request.processed_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(request)
        
        return request
    
    def reject_topup_request(
        self,
        request_id: int,
        admin_user_id: int,
        admin_notes: str = None
    ) -> TopUpRequest:
        """Reject manual top up request"""
        
        request = self.get_topup_request(request_id)
        
        if request.status != TopUpStatus.PENDING:
            raise ValidationError("Request sudah diproses sebelumnya")
        
        request.status = TopUpStatus.REJECTED
        request.admin_notes = admin_notes
        request.processed_by = admin_user_id
        request.processed_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(request)
        
        return request
    
    def get_pending_requests(
        self, 
        limit: int = 50,
        offset: int = 0
    ) -> list[TopUpRequest]:
        """Get all pending top up requests for admin"""
        return self.db.query(TopUpRequest).filter(
            TopUpRequest.status == TopUpStatus.PENDING
        ).order_by(TopUpRequest.created_at.asc()).offset(offset).limit(limit).all()
