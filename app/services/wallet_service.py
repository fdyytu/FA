from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.models.user import User
from app.models.wallet import (
    WalletTransaction, Transfer, TopUpRequest,
    TransactionType, TransactionStatus, PaymentMethod, TopUpStatus
)
from app.schemas.wallet import (
    TransferRequest, TopUpManualRequest, TopUpMidtransRequest,
    TopUpApprovalRequest
)
from app.services.midtrans_service import midtrans_service
from app.utils.exceptions import ValidationError, NotFoundError, InsufficientBalanceError
from typing import Optional, List, Dict, Any
from decimal import Decimal
import uuid
from datetime import datetime
import json

class WalletService:
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_balance(self, user_id: int) -> Decimal:
        """Get user's current balance"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundError("User not found")
        return user.balance
    
    def create_transaction_code(self, prefix: str = "TXN") -> str:
        """Generate unique transaction code"""
        return f"{prefix}-{uuid.uuid4().hex[:12].upper()}"
    
    def create_wallet_transaction(
        self,
        user_id: int,
        transaction_type: TransactionType,
        amount: Decimal,
        description: str = None,
        reference_id: str = None,
        metadata: Dict = None,
        status: TransactionStatus = TransactionStatus.PENDING
    ) -> WalletTransaction:
        """Create a wallet transaction record"""
        
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundError("User not found")
        
        balance_before = user.balance
        
        # Calculate balance after based on transaction type
        if transaction_type in [TransactionType.TOPUP_MANUAL, TransactionType.TOPUP_MIDTRANS, TransactionType.TRANSFER_RECEIVE, TransactionType.REFUND]:
            balance_after = balance_before + amount
        else:  # TRANSFER_SEND, PPOB_PAYMENT
            balance_after = balance_before - amount
            if balance_after < 0:
                raise InsufficientBalanceError("Insufficient balance")
        
        transaction = WalletTransaction(
            user_id=user_id,
            transaction_code=self.create_transaction_code(),
            transaction_type=transaction_type,
            amount=amount,
            balance_before=balance_before,
            balance_after=balance_after,
            status=status,
            description=description,
            reference_id=reference_id,
            meta_data=json.dumps(metadata) if metadata else None
        )
        
        self.db.add(transaction)
        
        # Update user balance if transaction is successful
        if status == TransactionStatus.SUCCESS:
            user.balance = balance_after
        
        self.db.commit()
        self.db.refresh(transaction)
        
        return transaction
    
    def update_transaction_status(
        self,
        transaction_id: int,
        status: TransactionStatus
    ) -> WalletTransaction:
        """Update transaction status and user balance"""
        
        transaction = self.db.query(WalletTransaction).filter(
            WalletTransaction.id == transaction_id
        ).first()
        
        if not transaction:
            raise NotFoundError("Transaction not found")
        
        old_status = transaction.status
        transaction.status = status
        
        # Update user balance if status changed to SUCCESS
        if old_status != TransactionStatus.SUCCESS and status == TransactionStatus.SUCCESS:
            user = self.db.query(User).filter(User.id == transaction.user_id).first()
            user.balance = transaction.balance_after
        
        self.db.commit()
        self.db.refresh(transaction)
        
        return transaction
    
    def transfer_money(
        self,
        sender_id: int,
        transfer_request: TransferRequest
    ) -> Transfer:
        """Transfer money between users"""
        
        # Get sender
        sender = self.db.query(User).filter(User.id == sender_id).first()
        if not sender:
            raise NotFoundError("Sender not found")
        
        # Get receiver by username
        receiver = self.db.query(User).filter(
            User.username == transfer_request.receiver_username
        ).first()
        if not receiver:
            raise NotFoundError("Receiver not found")
        
        if sender.id == receiver.id:
            raise ValidationError("Cannot transfer to yourself")
        
        # Check sender balance
        if sender.balance < transfer_request.amount:
            raise InsufficientBalanceError("Insufficient balance")
        
        # Create transfer record
        transfer = Transfer(
            sender_id=sender.id,
            receiver_id=receiver.id,
            transfer_code=self.create_transaction_code("TRF"),
            amount=transfer_request.amount,
            description=transfer_request.description,
            status=TransactionStatus.PENDING
        )
        
        self.db.add(transfer)
        self.db.flush()  # Get transfer ID
        
        try:
            # Create sender transaction (debit)
            sender_transaction = self.create_wallet_transaction(
                user_id=sender.id,
                transaction_type=TransactionType.TRANSFER_SEND,
                amount=transfer_request.amount,
                description=f"Transfer to {receiver.username}",
                reference_id=transfer.transfer_code,
                status=TransactionStatus.SUCCESS
            )
            
            # Create receiver transaction (credit)
            receiver_transaction = self.create_wallet_transaction(
                user_id=receiver.id,
                transaction_type=TransactionType.TRANSFER_RECEIVE,
                amount=transfer_request.amount,
                description=f"Transfer from {sender.username}",
                reference_id=transfer.transfer_code,
                status=TransactionStatus.SUCCESS
            )
            
            # Update transfer with transaction IDs
            transfer.sender_transaction_id = sender_transaction.id
            transfer.receiver_transaction_id = receiver_transaction.id
            transfer.status = TransactionStatus.SUCCESS
            
            self.db.commit()
            self.db.refresh(transfer)
            
            return transfer
            
        except Exception as e:
            self.db.rollback()
            raise e
    
    def create_manual_topup_request(
        self,
        user_id: int,
        topup_request: TopUpManualRequest
    ) -> TopUpRequest:
        """Create manual top up request"""
        
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundError("User not found")
        
        request = TopUpRequest(
            user_id=user_id,
            request_code=self.create_transaction_code("TOPUP"),
            amount=topup_request.amount,
            payment_method=topup_request.payment_method,
            bank_name=topup_request.bank_name,
            account_number=topup_request.account_number,
            account_name=topup_request.account_name,
            notes=topup_request.notes,
            status=TopUpStatus.PENDING
        )
        
        self.db.add(request)
        self.db.commit()
        self.db.refresh(request)
        
        return request
    
    def create_midtrans_topup(
        self,
        user_id: int,
        topup_request: TopUpMidtransRequest
    ) -> Dict[str, Any]:
        """Create Midtrans top up payment"""
        
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundError("User not found")
        
        # Create top up request
        request = TopUpRequest(
            user_id=user_id,
            request_code=self.create_transaction_code("TOPUP"),
            amount=topup_request.amount,
            payment_method=PaymentMethod.MIDTRANS,
            status=TopUpStatus.PENDING
        )
        
        self.db.add(request)
        self.db.flush()  # Get request ID
        
        # Create Midtrans order
        order_id = f"TOPUP-{request.id}-{uuid.uuid4().hex[:8]}"
        request.midtrans_order_id = order_id
        
        customer_details = {
            'first_name': user.full_name,
            'email': user.email,
            'phone': user.phone_number or '08123456789'
        }
        
        # Create payment token
        payment_result = midtrans_service.create_payment_token(
            order_id=order_id,
            amount=topup_request.amount,
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
    
    def process_topup_approval(
        self,
        request_id: int,
        approval_request: TopUpApprovalRequest,
        admin_user_id: int
    ) -> TopUpRequest:
        """Process manual top up approval/rejection"""
        
        request = self.db.query(TopUpRequest).filter(
            TopUpRequest.id == request_id
        ).first()
        
        if not request:
            raise NotFoundError("Top up request not found")
        
        if request.status != TopUpStatus.PENDING:
            raise ValidationError("Request has already been processed")
        
        request.status = approval_request.status
        request.admin_notes = approval_request.admin_notes
        request.processed_by = admin_user_id
        request.processed_at = datetime.utcnow()
        
        # If approved, create wallet transaction
        if approval_request.status == TopUpStatus.APPROVED:
            wallet_transaction = self.create_wallet_transaction(
                user_id=request.user_id,
                transaction_type=TransactionType.TOPUP_MANUAL,
                amount=request.amount,
                description=f"Manual top up - {request.request_code}",
                reference_id=request.request_code,
                status=TransactionStatus.SUCCESS
            )
            request.wallet_transaction_id = wallet_transaction.id
        
        self.db.commit()
        self.db.refresh(request)
        
        return request
    
    def get_transaction_history(
        self,
        user_id: int,
        page: int = 1,
        per_page: int = 20,
        transaction_type: Optional[TransactionType] = None
    ) -> Dict[str, Any]:
        """Get user's transaction history"""
        
        query = self.db.query(WalletTransaction).filter(
            WalletTransaction.user_id == user_id
        )
        
        if transaction_type:
            query = query.filter(WalletTransaction.transaction_type == transaction_type)
        
        total_count = query.count()
        
        transactions = query.order_by(
            WalletTransaction.created_at.desc()
        ).offset((page - 1) * per_page).limit(per_page).all()
        
        total_pages = (total_count + per_page - 1) // per_page
        
        return {
            'transactions': transactions,
            'total_count': total_count,
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages
        }
    
    def get_pending_topup_requests(
        self,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """Get pending top up requests for admin"""
        
        query = self.db.query(TopUpRequest).filter(
            TopUpRequest.status == TopUpStatus.PENDING
        )
        
        total_count = query.count()
        
        requests = query.order_by(
            TopUpRequest.created_at.desc()
        ).offset((page - 1) * per_page).limit(per_page).all()
        
        total_pages = (total_count + per_page - 1) // per_page
        
        return {
            'requests': requests,
            'total_count': total_count,
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages
        }
    
    def process_midtrans_notification(
        self,
        notification_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process Midtrans payment notification"""
        
        verification_result = midtrans_service.verify_notification(notification_data)
        
        if not verification_result['success']:
            return {'success': False, 'error': verification_result['error']}
        
        order_id = verification_result['order_id']
        status = verification_result['status']
        
        # Find top up request by order ID
        request = self.db.query(TopUpRequest).filter(
            TopUpRequest.midtrans_order_id == order_id
        ).first()
        
        if not request:
            return {'success': False, 'error': 'Top up request not found'}
        
        # Update request status based on payment status
        if status == 'success':
            request.status = TopUpStatus.APPROVED
            request.processed_at = datetime.utcnow()
            
            # Create wallet transaction
            wallet_transaction = self.create_wallet_transaction(
                user_id=request.user_id,
                transaction_type=TransactionType.TOPUP_MIDTRANS,
                amount=request.amount,
                description=f"Midtrans top up - {request.request_code}",
                reference_id=request.request_code,
                metadata={'midtrans_data': verification_result['raw_data']},
                status=TransactionStatus.SUCCESS
            )
            request.wallet_transaction_id = wallet_transaction.id
            
        elif status == 'failed':
            request.status = TopUpStatus.REJECTED
            request.processed_at = datetime.utcnow()
            request.admin_notes = "Payment failed"
        
        # Store Midtrans transaction ID
        if 'transaction_id' in verification_result['raw_data']:
            request.midtrans_transaction_id = verification_result['raw_data']['transaction_id']
        
        self.db.commit()
        
        return {'success': True, 'status': status, 'request_id': request.id}
