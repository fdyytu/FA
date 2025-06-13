from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from app.shared.base_classes.base_repository import BaseRepository
from app.domains.admin.models.admin import (
    Admin, AdminConfig, PPOBMarginConfig, AdminAuditLog, AdminNotificationSetting
)
from app.domains.auth.models.user import User
from app.domains.ppob.models.ppob import PPOBProduct, PPOBTransaction
from app.models.transaction import Transaction


class AdminRepository(BaseRepository[Admin]):
    """
    Repository untuk admin - Single Responsibility: Data access untuk admin
    """
    
    def __init__(self, db: Session):
        super().__init__(db, Admin)
    
    def get_by_username(self, username: str) -> Optional[Admin]:
        """Ambil admin berdasarkan username"""
        return self.db.query(Admin).filter(Admin.username == username).first()
    
    def get_by_email(self, email: str) -> Optional[Admin]:
        """Ambil admin berdasarkan email"""
        return self.db.query(Admin).filter(Admin.email == email).first()
    
    def update_last_login(self, admin_id: str) -> None:
        """Update waktu login terakhir"""
        self.db.query(Admin).filter(Admin.id == admin_id).update({
            "last_login": datetime.utcnow()
        })
        self.db.commit()


class AdminConfigRepository(BaseRepository[AdminConfig]):
    """
    Repository untuk konfigurasi admin - Single Responsibility: Data access untuk config
    """
    
    def __init__(self, db: Session):
        super().__init__(db, AdminConfig)
    
    def get_by_key(self, config_key: str) -> Optional[AdminConfig]:
        """Ambil konfigurasi berdasarkan key"""
        return self.db.query(AdminConfig).filter(
            AdminConfig.config_key == config_key,
            AdminConfig.is_active == True
        ).first()
    
    def get_active_configs(self) -> List[AdminConfig]:
        """Ambil semua konfigurasi aktif"""
        return self.db.query(AdminConfig).filter(
            AdminConfig.is_active == True
        ).all()
    
    def update_config_value(self, config_key: str, config_value: str) -> bool:
        """Update nilai konfigurasi"""
        result = self.db.query(AdminConfig).filter(
            AdminConfig.config_key == config_key
        ).update({"config_value": config_value})
        self.db.commit()
        return result > 0


class PPOBMarginRepository(BaseRepository[PPOBMarginConfig]):
    """
    Repository untuk margin PPOB - Single Responsibility: Data access untuk margin
    """
    
    def __init__(self, db: Session):
        super().__init__(db, PPOBMarginConfig)
    
    def get_by_category(self, category: str) -> List[PPOBMarginConfig]:
        """Ambil margin berdasarkan kategori"""
        return self.db.query(PPOBMarginConfig).filter(
            PPOBMarginConfig.category == category,
            PPOBMarginConfig.is_active == True
        ).all()
    
    def get_by_product_code(self, product_code: str) -> Optional[PPOBMarginConfig]:
        """Ambil margin berdasarkan kode produk"""
        return self.db.query(PPOBMarginConfig).filter(
            PPOBMarginConfig.product_code == product_code,
            PPOBMarginConfig.is_active == True
        ).first()
    
    def get_global_margin(self, category: str) -> Optional[PPOBMarginConfig]:
        """Ambil margin global untuk kategori"""
        return self.db.query(PPOBMarginConfig).filter(
            PPOBMarginConfig.category == category,
            PPOBMarginConfig.product_code.is_(None),
            PPOBMarginConfig.is_active == True
        ).first()


class UserManagementRepository:
    """
    Repository untuk manajemen user - Single Responsibility: Data access untuk user management
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_users_with_pagination(
        self, 
        skip: int = 0, 
        limit: int = 10,
        search: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> tuple[List[User], int]:
        """Ambil user dengan pagination dan filter"""
        query = self.db.query(User)
        
        # Apply filters
        if search:
            query = query.filter(
                or_(
                    User.username.ilike(f"%{search}%"),
                    User.email.ilike(f"%{search}%"),
                    User.full_name.ilike(f"%{search}%")
                )
            )
        
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        
        total = query.count()
        users = query.offset(skip).limit(limit).all()
        
        return users, total
    
    def get_user_stats(self) -> Dict[str, int]:
        """Ambil statistik user"""
        total_users = self.db.query(User).count()
        active_users = self.db.query(User).filter(User.is_active == True).count()
        inactive_users = total_users - active_users
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "inactive_users": inactive_users
        }


class ProductManagementRepository:
    """
    Repository untuk manajemen produk - Single Responsibility: Data access untuk product management
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_products_with_pagination(
        self,
        skip: int = 0,
        limit: int = 10,
        search: Optional[str] = None,
        category: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> tuple[List[PPOBProduct], int]:
        """Ambil produk dengan pagination dan filter"""
        query = self.db.query(PPOBProduct)
        
        # Apply filters
        if search:
            query = query.filter(
                or_(
                    PPOBProduct.product_code.ilike(f"%{search}%"),
                    PPOBProduct.product_name.ilike(f"%{search}%")
                )
            )
        
        if category:
            query = query.filter(PPOBProduct.category == category)
        
        if is_active is not None:
            query = query.filter(PPOBProduct.is_active == str(is_active).lower())
        
        total = query.count()
        products = query.offset(skip).limit(limit).all()
        
        return products, total
    
    def get_product_categories(self) -> List[str]:
        """Ambil semua kategori produk"""
        categories = self.db.query(PPOBProduct.category).distinct().all()
        return [cat[0] for cat in categories]


class DashboardRepository:
    """
    Repository untuk dashboard - Single Responsibility: Data access untuk dashboard
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Ambil statistik untuk dashboard"""
        # User stats
        total_users = self.db.query(User).count()
        active_users = self.db.query(User).filter(User.is_active == True).count()
        
        # Transaction stats
        total_transactions = self.db.query(PPOBTransaction).count()
        pending_transactions = self.db.query(PPOBTransaction).filter(
            PPOBTransaction.status == "pending"
        ).count()
        failed_transactions = self.db.query(PPOBTransaction).filter(
            PPOBTransaction.status == "failed"
        ).count()
        
        # Revenue stats
        total_revenue = self.db.query(
            func.sum(PPOBTransaction.total_amount)
        ).filter(
            PPOBTransaction.status == "success"
        ).scalar() or 0
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "total_transactions": total_transactions,
            "total_revenue": float(total_revenue),
            "pending_transactions": pending_transactions,
            "failed_transactions": failed_transactions
        }
    
    def get_recent_transactions(self, limit: int = 10) -> List[PPOBTransaction]:
        """Ambil transaksi terbaru"""
        return self.db.query(PPOBTransaction).order_by(
            desc(PPOBTransaction.created_at)
        ).limit(limit).all()
    
    def get_transaction_trends(self, days: int = 7) -> List[Dict[str, Any]]:
        """Ambil trend transaksi"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        results = self.db.query(
            func.date(PPOBTransaction.created_at).label('date'),
            func.count(PPOBTransaction.id).label('count'),
            func.sum(PPOBTransaction.total_amount).label('amount')
        ).filter(
            PPOBTransaction.created_at >= start_date
        ).group_by(
            func.date(PPOBTransaction.created_at)
        ).all()
        
        return [
            {
                "date": str(result.date),
                "count": result.count,
                "amount": float(result.amount or 0)
            }
            for result in results
        ]
    
    def get_top_products(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Ambil produk terpopuler"""
        results = self.db.query(
            PPOBTransaction.product_code,
            PPOBTransaction.product_name,
            func.count(PPOBTransaction.id).label('transaction_count'),
            func.sum(PPOBTransaction.total_amount).label('total_amount')
        ).filter(
            PPOBTransaction.status == "success"
        ).group_by(
            PPOBTransaction.product_code,
            PPOBTransaction.product_name
        ).order_by(
            desc(func.count(PPOBTransaction.id))
        ).limit(limit).all()
        
        return [
            {
                "product_code": result.product_code,
                "product_name": result.product_name,
                "transaction_count": result.transaction_count,
                "total_amount": float(result.total_amount or 0)
            }
            for result in results
        ]


class AuditLogRepository(BaseRepository[AdminAuditLog]):
    """
    Repository untuk audit log - Single Responsibility: Data access untuk audit log
    """
    
    def __init__(self, db: Session):
        super().__init__(db, AdminAuditLog)
    
    def create_log(
        self,
        admin_id: str,
        action: str,
        resource: str,
        resource_id: Optional[str] = None,
        old_values: Optional[str] = None,
        new_values: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AdminAuditLog:
        """Buat log audit baru"""
        audit_log = AdminAuditLog(
            admin_id=admin_id,
            action=action,
            resource=resource,
            resource_id=resource_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        self.db.add(audit_log)
        self.db.commit()
        self.db.refresh(audit_log)
        
        return audit_log
    
    def get_logs_with_pagination(
        self,
        skip: int = 0,
        limit: int = 10,
        admin_id: Optional[str] = None,
        action: Optional[str] = None,
        resource: Optional[str] = None
    ) -> tuple[List[AdminAuditLog], int]:
        """Ambil audit log dengan pagination dan filter"""
        query = self.db.query(AdminAuditLog)
        
        if admin_id:
            query = query.filter(AdminAuditLog.admin_id == admin_id)
        
        if action:
            query = query.filter(AdminAuditLog.action == action)
        
        if resource:
            query = query.filter(AdminAuditLog.resource == resource)
        
        total = query.count()
        logs = query.order_by(desc(AdminAuditLog.created_at)).offset(skip).limit(limit).all()
        
        return logs, total
