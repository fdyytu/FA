"""
Payment Factory - Mengikuti Factory Pattern dan Dependency Injection
Mengelola berbagai payment methods dengan clean architecture
"""
from typing import Dict, Any, Protocol
from decimal import Decimal
from sqlalchemy.orm import Session
import uuid

from app.domains.payment.services.midtrans_service import MidtransService
from app.domains.payment.services.manual_topup_service import ManualTopUpService
from app.models.wallet import PaymentMethod, TopUpRequest, TopUpStatus
from app.models.user import User
from app.utils.exceptions import ValidationError, NotFoundError


class PaymentServiceProtocol(Protocol):
    """Protocol untuk payment services - mengikuti Interface Segregation"""
    
    def process_payment(self, user_id: int, amount: Decimal, **kwargs) -> Dict[str, Any]:
        """Process payment dengan method tertentu"""
        ...


class MidtransPaymentService:
    """Wrapper untuk Midtrans payment - mengikuti Adapter Pattern"""
    
    def __init__(self, db: Session):
        self.db = db
        self.midtrans_service = MidtransService()
    
    def process_payment(self, user_id: int, amount: Decimal, **kwargs) -> Dict[str, Any]:
        """Process Midtrans payment"""
        
        # Validasi user
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundError("User tidak ditemukan")
        
        # Create top up request
        request = TopUpRequest(
            user_id=user_id,
            request_code=self._generate_request_code(),
            amount=amount,
            payment_method=PaymentMethod.MIDTRANS,
            status=TopUpStatus.PENDING
        )
        
        self.db.add(request)
        self.db.flush()  # Get request ID
        
        # Create Midtrans order
        order_id = f"TOPUP-{request.id}-{uuid.uuid4().hex[:8]}"
        request.midtrans_order_id = order_id
        
        customer_details = {
            'first_name': user.full_name or user.username,
            'email': user.email,
            'phone': user.phone_number or '08123456789'
        }
        
        # Create payment token
        payment_result = self.midtrans_service.create_payment_token(
            order_id=order_id,
            amount=amount,
            customer_details=customer_details
        )
        
        if not payment_result['success']:
            self.db.rollback()
            raise ValidationError(f"Failed to create payment: {payment_result['error']}")
        
        self.db.commit()
        self.db.refresh(request)
        
        return {
            'request_code': request.request_code,
            'amount': request.amount,
            'midtrans_order_id': order_id,
            'payment_url': payment_result['redirect_url'],
            'status': request.status
        }
    
    def _generate_request_code(self, prefix: str = "TOPUP") -> str:
        """Generate unique request code"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_id = str(uuid.uuid4())[:8].upper()
        return f"{prefix}-{timestamp}-{unique_id}"


class ManualPaymentService:
    """Wrapper untuk manual payment - mengikuti Adapter Pattern"""
    
    def __init__(self, db: Session):
        self.manual_service = ManualTopUpService(db)
    
    def process_payment(self, user_id: int, amount: Decimal, **kwargs) -> Dict[str, Any]:
        """Process manual payment"""
        
        payment_method = kwargs.get('payment_method', PaymentMethod.BANK_TRANSFER)
        bank_name = kwargs.get('bank_name')
        account_number = kwargs.get('account_number')
        account_name = kwargs.get('account_name')
        notes = kwargs.get('notes')
        
        request = self.manual_service.create_topup_request(
            user_id=user_id,
            amount=amount,
            payment_method=payment_method,
            bank_name=bank_name,
            account_number=account_number,
            account_name=account_name,
            notes=notes
        )
        
        return {
            'request_code': request.request_code,
            'amount': request.amount,
            'payment_method': request.payment_method,
            'status': request.status,
            'bank_name': request.bank_name,
            'account_number': request.account_number
        }


class PaymentFactory:
    """Factory untuk membuat payment services - mengikuti Factory Pattern"""
    
    def __init__(self, db: Session):
        self.db = db
        self._services = {
            PaymentMethod.MIDTRANS: MidtransPaymentService,
            PaymentMethod.BANK_TRANSFER: ManualPaymentService,
            PaymentMethod.E_WALLET: ManualPaymentService,
            PaymentMethod.VIRTUAL_ACCOUNT: ManualPaymentService,
        }
    
    def get_payment_service(self, payment_method: PaymentMethod) -> PaymentServiceProtocol:
        """Get payment service berdasarkan method - mengikuti Factory Pattern"""
        
        service_class = self._services.get(payment_method)
        if not service_class:
            raise ValidationError(f"Payment method {payment_method} tidak didukung")
        
        return service_class(self.db)
    
    def process_payment(
        self, 
        payment_method: PaymentMethod, 
        user_id: int, 
        amount: Decimal, 
        **kwargs
    ) -> Dict[str, Any]:
        """Process payment dengan method tertentu"""
        
        service = self.get_payment_service(payment_method)
        return service.process_payment(user_id, amount, **kwargs)
