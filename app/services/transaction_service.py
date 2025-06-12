from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc, text
from datetime import datetime, date, timedelta
from app.models.transaction import Transaction, DailyMutation, TransactionType, TransactionStatus
from app.models.user import User
from app.schemas.transaction import (
    TransactionCreate, TransactionUpdate, TransactionResponse,
    TransactionHistoryResponse, DailyMutationResponse, TransactionSummaryResponse,
    TransactionFilterRequest
)
from app.utils.exceptions import HTTPException
import logging
import json
import uuid

logger = logging.getLogger(__name__)

class TransactionService:
    """Service untuk mengelola transaksi - mengikuti prinsip Single Responsibility"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def _generate_transaction_code(self) -> str:
        """Generate kode transaksi unik - mengikuti prinsip DRY"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_id = str(uuid.uuid4())[:8].upper()
        return f"TRX{timestamp}{unique_id}"
    
    async def create_transaction(self, transaction_data: TransactionCreate) -> TransactionResponse:
        """Membuat transaksi baru"""
        try:
            # Cek apakah user ada
            user = self.db.query(User).filter(User.id == transaction_data.user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User tidak ditemukan")
            
            # Generate kode transaksi
            transaction_code = self._generate_transaction_code()
            
            # Hitung total amount
            total_amount = transaction_data.amount + transaction_data.admin_fee
            
            # Buat transaksi baru
            db_transaction = Transaction(
                user_id=transaction_data.user_id,
                transaction_code=transaction_code,
                transaction_type=transaction_data.transaction_type,
                amount=transaction_data.amount,
                admin_fee=transaction_data.admin_fee,
                total_amount=total_amount,
                description=transaction_data.description,
                reference_id=transaction_data.reference_id,
                metadata=transaction_data.metadata
            )
            
            self.db.add(db_transaction)
            self.db.commit()
            self.db.refresh(db_transaction)
            
            logger.info(f"Transaksi berhasil dibuat: {transaction_code}")
            return TransactionResponse.from_orm(db_transaction)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating transaction: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Gagal membuat transaksi: {str(e)}")
    
    async def update_transaction(self, transaction_id: int, update_data: TransactionUpdate) -> TransactionResponse:
        """Update status transaksi"""
        try:
            transaction = self.db.query(Transaction).filter(Transaction.id == transaction_id).first()
            if not transaction:
                raise HTTPException(status_code=404, detail="Transaksi tidak ditemukan")
            
            # Update data yang tidak None
            update_fields = update_data.dict(exclude_unset=True)
            for field, value in update_fields.items():
                setattr(transaction, field, value)
            
            # Set processed_at jika status berubah ke success atau failed
            if update_data.status in [TransactionStatus.SUCCESS, TransactionStatus.FAILED]:
                transaction.processed_at = datetime.now()
            
            self.db.commit()
            self.db.refresh(transaction)
            
            logger.info(f"Transaksi berhasil diupdate: {transaction.transaction_code}")
            return TransactionResponse.from_orm(transaction)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating transaction: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Gagal update transaksi: {str(e)}")
    
    async def get_transaction_history(self, filter_request: TransactionFilterRequest) -> List[TransactionHistoryResponse]:
        """Mendapatkan riwayat transaksi dengan filter"""
        try:
            query = self.db.query(Transaction)
            
            # Apply filters
            if filter_request.user_id:
                query = query.filter(Transaction.user_id == filter_request.user_id)
            
            if filter_request.transaction_type:
                query = query.filter(Transaction.transaction_type == filter_request.transaction_type)
            
            if filter_request.status:
                query = query.filter(Transaction.status == filter_request.status)
            
            if filter_request.start_date:
                query = query.filter(Transaction.created_at >= filter_request.start_date)
            
            if filter_request.end_date:
                query = query.filter(Transaction.created_at <= filter_request.end_date)
            
            # Pagination
            offset = (filter_request.page - 1) * filter_request.limit
            transactions = query.order_by(desc(Transaction.created_at)).offset(offset).limit(filter_request.limit).all()
            
            return [TransactionHistoryResponse.from_orm(t) for t in transactions]
            
        except Exception as e:
            logger.error(f"Error getting transaction history: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Gagal mengambil riwayat transaksi: {str(e)}")
    
    async def get_transaction_summary(self, user_id: Optional[int] = None, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> TransactionSummaryResponse:
        """Mendapatkan ringkasan transaksi"""
        try:
            query = self.db.query(Transaction)
            
            # Apply filters
            if user_id:
                query = query.filter(Transaction.user_id == user_id)
            
            if start_date:
                query = query.filter(Transaction.created_at >= start_date)
            
            if end_date:
                query = query.filter(Transaction.created_at <= end_date)
            
            transactions = query.all()
            
            # Hitung statistik
            total_transactions = len(transactions)
            total_amount = sum(float(t.amount) for t in transactions)
            total_fee = sum(float(t.admin_fee) for t in transactions)
            success_count = len([t for t in transactions if t.status == TransactionStatus.SUCCESS])
            success_rate = (success_count / total_transactions * 100) if total_transactions > 0 else 0
            
            # Breakdown by type
            transaction_by_type = {}
            for t in transactions:
                type_name = t.transaction_type.value
                transaction_by_type[type_name] = transaction_by_type.get(type_name, 0) + 1
            
            # Breakdown by status
            transaction_by_status = {}
            for t in transactions:
                status_name = t.status.value
                transaction_by_status[status_name] = transaction_by_status.get(status_name, 0) + 1
            
            return TransactionSummaryResponse(
                total_transactions=total_transactions,
                total_amount=total_amount,
                total_fee=total_fee,
                success_rate=success_rate,
                transaction_by_type=transaction_by_type,
                transaction_by_status=transaction_by_status
            )
            
        except Exception as e:
            logger.error(f"Error getting transaction summary: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Gagal mengambil ringkasan transaksi: {str(e)}")

class DailyMutationService:
    """Service untuk mengelola mutasi harian - mengikuti prinsip Single Responsibility"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def generate_daily_mutation(self, target_date: date) -> DailyMutationResponse:
        """Generate mutasi harian untuk tanggal tertentu"""
        try:
            # Cek apakah mutasi untuk tanggal ini sudah ada
            existing_mutation = self.db.query(DailyMutation).filter(
                func.date(DailyMutation.mutation_date) == target_date
            ).first()
            
            if existing_mutation:
                logger.info(f"Mutasi harian untuk {target_date} sudah ada")
                return DailyMutationResponse.from_orm(existing_mutation)
            
            # Ambil semua transaksi untuk tanggal tersebut
            start_datetime = datetime.combine(target_date, datetime.min.time())
            end_datetime = datetime.combine(target_date, datetime.max.time())
            
            transactions = self.db.query(Transaction).filter(
                and_(
                    Transaction.created_at >= start_datetime,
                    Transaction.created_at <= end_datetime
                )
            ).all()
            
            # Hitung statistik
            total_transactions = len(transactions)
            total_amount = sum(float(t.amount) for t in transactions)
            total_fee = sum(float(t.admin_fee) for t in transactions)
            success_count = len([t for t in transactions if t.status == TransactionStatus.SUCCESS])
            failed_count = len([t for t in transactions if t.status == TransactionStatus.FAILED])
            pending_count = len([t for t in transactions if t.status == TransactionStatus.PENDING])
            
            # Breakdown by type
            transaction_types = {}
            for t in transactions:
                type_name = t.transaction_type.value
                transaction_types[type_name] = transaction_types.get(type_name, 0) + 1
            
            # Buat mutasi harian
            daily_mutation = DailyMutation(
                mutation_date=start_datetime,
                total_transactions=total_transactions,
                total_amount=total_amount,
                total_fee=total_fee,
                success_count=success_count,
                failed_count=failed_count,
                pending_count=pending_count,
                transaction_types=json.dumps(transaction_types)
            )
            
            self.db.add(daily_mutation)
            self.db.commit()
            self.db.refresh(daily_mutation)
            
            logger.info(f"Mutasi harian berhasil dibuat untuk {target_date}")
            return DailyMutationResponse.from_orm(daily_mutation)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error generating daily mutation: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Gagal generate mutasi harian: {str(e)}")
    
    async def get_daily_mutations(self, start_date: date, end_date: date) -> List[DailyMutationResponse]:
        """Mendapatkan mutasi harian dalam rentang tanggal"""
        try:
            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = datetime.combine(end_date, datetime.max.time())
            
            mutations = self.db.query(DailyMutation).filter(
                and_(
                    DailyMutation.mutation_date >= start_datetime,
                    DailyMutation.mutation_date <= end_datetime
                )
            ).order_by(asc(DailyMutation.mutation_date)).all()
            
            return [DailyMutationResponse.from_orm(m) for m in mutations]
            
        except Exception as e:
            logger.error(f"Error getting daily mutations: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Gagal mengambil mutasi harian: {str(e)}")
    
    async def auto_generate_daily_mutations(self):
        """Auto generate mutasi harian untuk kemarin (untuk dijadwalkan)"""
        try:
            yesterday = date.today() - timedelta(days=1)
            await self.generate_daily_mutation(yesterday)
            logger.info(f"Auto generate mutasi harian berhasil untuk {yesterday}")
            
        except Exception as e:
            logger.error(f"Error auto generating daily mutation: {str(e)}")
            raise e
    
    async def get_mutation_summary(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Mendapatkan ringkasan mutasi dalam periode tertentu"""
        try:
            mutations = await self.get_daily_mutations(start_date, end_date)
            
            if not mutations:
                return {
                    "period": f"{start_date} - {end_date}",
                    "total_days": 0,
                    "total_transactions": 0,
                    "total_amount": 0,
                    "total_fee": 0,
                    "average_daily_transactions": 0,
                    "average_daily_amount": 0
                }
            
            total_transactions = sum(m.total_transactions for m in mutations)
            total_amount = sum(float(m.total_amount) for m in mutations)
            total_fee = sum(float(m.total_fee) for m in mutations)
            total_days = len(mutations)
            
            return {
                "period": f"{start_date} - {end_date}",
                "total_days": total_days,
                "total_transactions": total_transactions,
                "total_amount": total_amount,
                "total_fee": total_fee,
                "average_daily_transactions": total_transactions / total_days if total_days > 0 else 0,
                "average_daily_amount": total_amount / total_days if total_days > 0 else 0,
                "daily_breakdown": [
                    {
                        "date": m.mutation_date.date(),
                        "transactions": m.total_transactions,
                        "amount": float(m.total_amount),
                        "fee": float(m.total_fee)
                    } for m in mutations
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting mutation summary: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Gagal mengambil ringkasan mutasi: {str(e)}")
