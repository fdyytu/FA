from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from app.shared.base_classes.base_repository import BaseRepository
from app.domains.ppob.models.ppob import PPOBTransaction, PPOBProduct, PPOBCategory, TransactionStatus

class PPOBRepository(BaseRepository[PPOBTransaction]):
    """
    Repository untuk PPOB yang mengimplementasikan Repository Pattern.
    Menangani semua operasi database terkait PPOB.
    """
    
    def __init__(self, db: Session):
        super().__init__(db, PPOBTransaction)
    
    def get_products_by_category(self, category: PPOBCategory) -> List[PPOBProduct]:
        """Ambil produk berdasarkan kategori"""
        return self.db.query(PPOBProduct).filter(
            PPOBProduct.category == category,
            PPOBProduct.is_active == "1"
        ).all()
    
    def get_product_by_code(self, product_code: str) -> Optional[PPOBProduct]:
        """Ambil produk berdasarkan kode"""
        return self.db.query(PPOBProduct).filter(
            PPOBProduct.product_code == product_code,
            PPOBProduct.is_active == "1"
        ).first()
    
    def get_transaction_by_code(self, transaction_code: str) -> Optional[PPOBTransaction]:
        """Ambil transaksi berdasarkan kode"""
        return self.db.query(PPOBTransaction).filter(
            PPOBTransaction.transaction_code == transaction_code
        ).first()
    
    def get_user_transactions(
        self, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 10,
        status: Optional[TransactionStatus] = None,
        category: Optional[PPOBCategory] = None
    ) -> List[PPOBTransaction]:
        """Ambil transaksi user dengan filter"""
        query = self.db.query(PPOBTransaction).filter(
            PPOBTransaction.user_id == user_id
        )
        
        if status:
            query = query.filter(PPOBTransaction.status == status)
        
        if category:
            query = query.filter(PPOBTransaction.category == category)
        
        return query.order_by(desc(PPOBTransaction.created_at)).offset(skip).limit(limit).all()
    
    def count_user_transactions(
        self, 
        user_id: int,
        status: Optional[TransactionStatus] = None,
        category: Optional[PPOBCategory] = None
    ) -> int:
        """Hitung total transaksi user"""
        query = self.db.query(PPOBTransaction).filter(
            PPOBTransaction.user_id == user_id
        )
        
        if status:
            query = query.filter(PPOBTransaction.status == status)
        
        if category:
            query = query.filter(PPOBTransaction.category == category)
        
        return query.count()
    
    def get_transactions_by_status(self, status: TransactionStatus) -> List[PPOBTransaction]:
        """Ambil transaksi berdasarkan status"""
        return self.db.query(PPOBTransaction).filter(
            PPOBTransaction.status == status
        ).all()
    
    def get_pending_transactions(self, older_than_minutes: int = 30) -> List[PPOBTransaction]:
        """Ambil transaksi pending yang sudah lama"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=older_than_minutes)
        return self.db.query(PPOBTransaction).filter(
            PPOBTransaction.status == TransactionStatus.PENDING,
            PPOBTransaction.created_at < cutoff_time
        ).all()
    
    def get_transaction_stats(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Ambil statistik transaksi"""
        query = self.db.query(PPOBTransaction)
        
        if user_id:
            query = query.filter(PPOBTransaction.user_id == user_id)
        
        # Total transaksi
        total_transactions = query.count()
        
        # Transaksi berhasil
        success_transactions = query.filter(
            PPOBTransaction.status == TransactionStatus.SUCCESS
        ).count()
        
        # Total amount
        total_amount = query.filter(
            PPOBTransaction.status == TransactionStatus.SUCCESS
        ).with_entities(func.sum(PPOBTransaction.total_amount)).scalar() or 0
        
        # Transaksi hari ini
        today = datetime.utcnow().date()
        today_transactions = query.filter(
            func.date(PPOBTransaction.created_at) == today
        ).count()
        
        return {
            "total_transactions": total_transactions,
            "success_transactions": success_transactions,
            "failed_transactions": query.filter(
                PPOBTransaction.status == TransactionStatus.FAILED
            ).count(),
            "pending_transactions": query.filter(
                PPOBTransaction.status == TransactionStatus.PENDING
            ).count(),
            "total_amount": float(total_amount),
            "today_transactions": today_transactions,
            "success_rate": (success_transactions / total_transactions * 100) if total_transactions > 0 else 0
        }
    
    def get_popular_products(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Ambil produk yang paling sering digunakan"""
        result = self.db.query(
            PPOBTransaction.product_code,
            PPOBTransaction.product_name,
            PPOBTransaction.category,
            func.count(PPOBTransaction.id).label('transaction_count')
        ).filter(
            PPOBTransaction.status == TransactionStatus.SUCCESS
        ).group_by(
            PPOBTransaction.product_code,
            PPOBTransaction.product_name,
            PPOBTransaction.category
        ).order_by(
            desc('transaction_count')
        ).limit(limit).all()
        
        return [
            {
                "product_code": row.product_code,
                "product_name": row.product_name,
                "category": row.category.value,
                "transaction_count": row.transaction_count
            }
            for row in result
        ]
    
    def get_monthly_revenue(self, year: int, month: int) -> Dict[str, Any]:
        """Ambil revenue bulanan"""
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        result = self.db.query(
            func.sum(PPOBTransaction.total_amount).label('total_revenue'),
            func.count(PPOBTransaction.id).label('total_transactions')
        ).filter(
            PPOBTransaction.status == TransactionStatus.SUCCESS,
            PPOBTransaction.created_at >= start_date,
            PPOBTransaction.created_at < end_date
        ).first()
        
        return {
            "year": year,
            "month": month,
            "total_revenue": float(result.total_revenue or 0),
            "total_transactions": result.total_transactions or 0
        }
