from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import hashlib
from decimal import Decimal

from app.shared.base_classes.base_service import BaseService
from app.domains.admin.models.admin import Admin, AdminConfig, PPOBMarginConfig, MarginType
from app.domains.admin.repositories.admin_repository import (
    AdminRepository, AdminConfigRepository, PPOBMarginRepository,
    UserManagementRepository, ProductManagementRepository, 
    DashboardRepository, AuditLogRepository
)
from app.domains.admin.schemas.admin_schemas import (
    AdminCreate, AdminUpdate, AdminResponse, ConfigCreate, ConfigUpdate,
    MarginConfigCreate, MarginConfigUpdate, UserUpdateByAdmin,
    ProductCreate, ProductUpdate, DashboardResponse, PaginationParams
)
from app.common.security.auth_security import get_password_hash, verify_password
from app.domains.ppob.models.ppob import PPOBProduct
from app.domains.auth.models.user import User


class AdminAuthService(BaseService):
    """
    Service untuk autentikasi admin - Single Responsibility: Admin authentication
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.admin_repo = AdminRepository(db)
        self.audit_repo = AuditLogRepository(db)
    
    def authenticate_admin(self, username: str, password: str) -> Optional[Admin]:
        """Autentikasi admin"""
        admin = self.admin_repo.get_by_username(username)
        if not admin:
            return None
        
        if not verify_password(password, admin.hashed_password):
            return None
        
        if not admin.is_active:
            return None
        
        # Update last login
        self.admin_repo.update_last_login(admin.id)
        
        # Log login activity
        self.audit_repo.create_log(
            admin_id=admin.id,
            action="LOGIN",
            resource="admin",
            resource_id=admin.id
        )
        
        return admin
    
    def create_admin(self, admin_data: AdminCreate, creator_admin_id: str) -> Admin:
        """Buat admin baru"""
        # Check if username or email already exists
        if self.admin_repo.get_by_username(admin_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username sudah digunakan"
            )
        
        if self.admin_repo.get_by_email(admin_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email sudah digunakan"
            )
        
        # Create admin
        admin = Admin(
            username=admin_data.username,
            email=admin_data.email,
            full_name=admin_data.full_name,
            phone_number=admin_data.phone_number,
            role=admin_data.role,
            hashed_password=get_password_hash(admin_data.password)
        )
        
        created_admin = self.admin_repo.create(admin)
        
        # Log creation
        self.audit_repo.create_log(
            admin_id=creator_admin_id,
            action="CREATE",
            resource="admin",
            resource_id=created_admin.id,
            new_values=json.dumps({
                "username": admin_data.username,
                "email": admin_data.email,
                "role": admin_data.role.value
            })
        )
        
        return created_admin


class AdminManagementService(BaseService):
    """
    Service untuk manajemen admin - Single Responsibility: Admin management
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.admin_repo = AdminRepository(db)
        self.audit_repo = AuditLogRepository(db)
    
    def get_admins(self, skip: int = 0, limit: int = 10) -> tuple[List[Admin], int]:
        """Ambil daftar admin dengan pagination"""
        return self.admin_repo.get_all_with_pagination(skip, limit)
    
    def get_admin_by_id(self, admin_id: str) -> Admin:
        """Ambil admin berdasarkan ID"""
        admin = self.admin_repo.get_by_id(admin_id)
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admin tidak ditemukan"
            )
        return admin
    
    def update_admin(
        self, 
        admin_id: str, 
        admin_data: AdminUpdate, 
        updater_admin_id: str
    ) -> Admin:
        """Update admin"""
        admin = self.get_admin_by_id(admin_id)
        
        # Store old values for audit
        old_values = {
            "full_name": admin.full_name,
            "email": admin.email,
            "phone_number": admin.phone_number,
            "role": admin.role.value if admin.role else None,
            "is_active": admin.is_active
        }
        
        # Update fields
        update_data = admin_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(admin, field, value)
        
        updated_admin = self.admin_repo.update(admin)
        
        # Log update
        self.audit_repo.create_log(
            admin_id=updater_admin_id,
            action="UPDATE",
            resource="admin",
            resource_id=admin_id,
            old_values=json.dumps(old_values),
            new_values=json.dumps(update_data)
        )
        
        return updated_admin
    
    def delete_admin(self, admin_id: str, deleter_admin_id: str) -> bool:
        """Hapus admin (soft delete)"""
        admin = self.get_admin_by_id(admin_id)
        
        # Prevent self-deletion
        if admin_id == deleter_admin_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tidak dapat menghapus akun sendiri"
            )
        
        result = self.admin_repo.delete(admin_id)
        
        if result:
            # Log deletion
            self.audit_repo.create_log(
                admin_id=deleter_admin_id,
                action="DELETE",
                resource="admin",
                resource_id=admin_id
            )
        
        return result


class ConfigurationService(BaseService):
    """
    Service untuk manajemen konfigurasi - Single Responsibility: Configuration management
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.config_repo = AdminConfigRepository(db)
        self.audit_repo = AuditLogRepository(db)
    
    def get_config(self, config_key: str) -> Optional[AdminConfig]:
        """Ambil konfigurasi berdasarkan key"""
        return self.config_repo.get_by_key(config_key)
    
    def get_all_configs(self, skip: int = 0, limit: int = 10) -> tuple[List[AdminConfig], int]:
        """Ambil semua konfigurasi"""
        return self.config_repo.get_all_with_pagination(skip, limit)
    
    def create_config(self, config_data: ConfigCreate, admin_id: str) -> AdminConfig:
        """Buat konfigurasi baru"""
        # Check if key already exists
        if self.config_repo.get_by_key(config_data.config_key):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Konfigurasi dengan key tersebut sudah ada"
            )
        
        config = AdminConfig(**config_data.dict())
        created_config = self.config_repo.create(config)
        
        # Log creation
        self.audit_repo.create_log(
            admin_id=admin_id,
            action="CREATE",
            resource="config",
            resource_id=created_config.id,
            new_values=json.dumps(config_data.dict())
        )
        
        return created_config
    
    def update_config(
        self, 
        config_id: str, 
        config_data: ConfigUpdate, 
        admin_id: str
    ) -> AdminConfig:
        """Update konfigurasi"""
        config = self.config_repo.get_by_id(config_id)
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Konfigurasi tidak ditemukan"
            )
        
        # Store old values
        old_values = {
            "config_value": config.config_value,
            "description": config.description,
            "is_active": config.is_active
        }
        
        # Update fields
        update_data = config_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(config, field, value)
        
        updated_config = self.config_repo.update(config)
        
        # Log update
        self.audit_repo.create_log(
            admin_id=admin_id,
            action="UPDATE",
            resource="config",
            resource_id=config_id,
            old_values=json.dumps(old_values),
            new_values=json.dumps(update_data)
        )
        
        return updated_config


class MarginManagementService(BaseService):
    """
    Service untuk manajemen margin - Single Responsibility: Margin management
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.margin_repo = PPOBMarginRepository(db)
        self.audit_repo = AuditLogRepository(db)
    
    def calculate_price_with_margin(
        self, 
        base_price: Decimal, 
        category: str, 
        product_code: Optional[str] = None
    ) -> Decimal:
        """Hitung harga dengan margin - KISS principle: Simple calculation"""
        # Try to get product-specific margin first
        margin_config = None
        if product_code:
            margin_config = self.margin_repo.get_by_product_code(product_code)
        
        # If no product-specific margin, get category margin
        if not margin_config:
            margin_config = self.margin_repo.get_global_margin(category)
        
        # If no margin config found, return base price
        if not margin_config:
            return base_price
        
        # Calculate margin
        if margin_config.margin_type == MarginType.PERCENTAGE:
            margin_amount = base_price * (margin_config.margin_value / 100)
        else:  # NOMINAL
            margin_amount = margin_config.margin_value
        
        return base_price + margin_amount
    
    def create_margin_config(
        self, 
        margin_data: MarginConfigCreate, 
        admin_id: str
    ) -> PPOBMarginConfig:
        """Buat konfigurasi margin baru"""
        margin_config = PPOBMarginConfig(**margin_data.dict())
        created_config = self.margin_repo.create(margin_config)
        
        # Log creation
        self.audit_repo.create_log(
            admin_id=admin_id,
            action="CREATE",
            resource="margin_config",
            resource_id=created_config.id,
            new_values=json.dumps(margin_data.dict(), default=str)
        )
        
        return created_config
    
    def update_margin_config(
        self,
        config_id: str,
        margin_data: MarginConfigUpdate,
        admin_id: str
    ) -> PPOBMarginConfig:
        """Update konfigurasi margin"""
        config = self.margin_repo.get_by_id(config_id)
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Konfigurasi margin tidak ditemukan"
            )
        
        # Store old values
        old_values = {
            "margin_type": config.margin_type.value if config.margin_type else None,
            "margin_value": str(config.margin_value),
            "description": config.description,
            "is_active": config.is_active
        }
        
        # Update fields
        update_data = margin_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(config, field, value)
        
        updated_config = self.margin_repo.update(config)
        
        # Log update
        self.audit_repo.create_log(
            admin_id=admin_id,
            action="UPDATE",
            resource="margin_config",
            resource_id=config_id,
            old_values=json.dumps(old_values),
            new_values=json.dumps(update_data, default=str)
        )
        
        return updated_config


class UserManagementService(BaseService):
    """
    Service untuk manajemen user - Single Responsibility: User management by admin
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserManagementRepository(db)
        self.audit_repo = AuditLogRepository(db)
    
    def get_users(
        self,
        skip: int = 0,
        limit: int = 10,
        search: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> tuple[List[User], int]:
        """Ambil daftar user dengan filter"""
        return self.user_repo.get_users_with_pagination(skip, limit, search, is_active)
    
    def get_user_stats(self) -> Dict[str, int]:
        """Ambil statistik user"""
        return self.user_repo.get_user_stats()
    
    def update_user(
        self,
        user_id: str,
        user_data: UserUpdateByAdmin,
        admin_id: str
    ) -> User:
        """Update user oleh admin"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User tidak ditemukan"
            )
        
        # Store old values
        old_values = {
            "full_name": user.full_name,
            "email": user.email,
            "phone_number": user.phone_number,
            "is_active": user.is_active,
            "balance": str(user.balance)
        }
        
        # Update fields
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        self.db.commit()
        self.db.refresh(user)
        
        # Log update
        self.audit_repo.create_log(
            admin_id=admin_id,
            action="UPDATE",
            resource="user",
            resource_id=user_id,
            old_values=json.dumps(old_values),
            new_values=json.dumps(update_data, default=str)
        )
        
        return user


class ProductManagementService(BaseService):
    """
    Service untuk manajemen produk - Single Responsibility: Product management
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.product_repo = ProductManagementRepository(db)
        self.audit_repo = AuditLogRepository(db)
    
    def get_products(
        self,
        skip: int = 0,
        limit: int = 10,
        search: Optional[str] = None,
        category: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> tuple[List[PPOBProduct], int]:
        """Ambil daftar produk dengan filter"""
        return self.product_repo.get_products_with_pagination(
            skip, limit, search, category, is_active
        )
    
    def get_product_categories(self) -> List[str]:
        """Ambil semua kategori produk"""
        return self.product_repo.get_product_categories()
    
    def create_product(self, product_data: ProductCreate, admin_id: str) -> PPOBProduct:
        """Buat produk baru"""
        # Check if product code already exists
        existing_product = self.db.query(PPOBProduct).filter(
            PPOBProduct.product_code == product_data.product_code
        ).first()
        
        if existing_product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Kode produk sudah digunakan"
            )
        
        product = PPOBProduct(
            product_code=product_data.product_code,
            product_name=product_data.product_name,
            category=product_data.category,
            price=product_data.price,
            admin_fee=product_data.admin_fee,
            description=product_data.description,
            is_active="1" if product_data.is_active else "0"
        )
        
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        
        # Log creation
        self.audit_repo.create_log(
            admin_id=admin_id,
            action="CREATE",
            resource="product",
            resource_id=product.id,
            new_values=json.dumps(product_data.dict(), default=str)
        )
        
        return product
    
    def update_product(
        self,
        product_id: str,
        product_data: ProductUpdate,
        admin_id: str
    ) -> PPOBProduct:
        """Update produk"""
        product = self.db.query(PPOBProduct).filter(PPOBProduct.id == product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produk tidak ditemukan"
            )
        
        # Store old values
        old_values = {
            "product_name": product.product_name,
            "price": str(product.price),
            "admin_fee": str(product.admin_fee),
            "description": product.description,
            "is_active": product.is_active
        }
        
        # Update fields
        update_data = product_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if field == "is_active":
                setattr(product, field, "1" if value else "0")
            else:
                setattr(product, field, value)
        
        self.db.commit()
        self.db.refresh(product)
        
        # Log update
        self.audit_repo.create_log(
            admin_id=admin_id,
            action="UPDATE",
            resource="product",
            resource_id=product_id,
            old_values=json.dumps(old_values),
            new_values=json.dumps(update_data, default=str)
        )
        
        return product


class DashboardService(BaseService):
    """
    Service untuk dashboard - Single Responsibility: Dashboard data aggregation
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.dashboard_repo = DashboardRepository(db)
    
    def get_dashboard_data(self) -> DashboardResponse:
        """Ambil data dashboard lengkap"""
        # Get statistics
        stats = self.dashboard_repo.get_dashboard_stats()
        
        # Get recent transactions
        recent_transactions = self.dashboard_repo.get_recent_transactions(10)
        recent_transactions_data = [
            {
                "id": tx.id,
                "transaction_code": tx.transaction_code,
                "product_name": tx.product_name,
                "amount": float(tx.total_amount),
                "status": tx.status.value if tx.status else "unknown",
                "created_at": tx.created_at.isoformat()
            }
            for tx in recent_transactions
        ]
        
        # Get transaction trends
        transaction_trends = self.dashboard_repo.get_transaction_trends(7)
        
        # Get top products
        top_products = self.dashboard_repo.get_top_products(5)
        
        return DashboardResponse(
            stats=stats,
            recent_transactions=recent_transactions_data,
            transaction_trends=transaction_trends,
            top_products=top_products
        )
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Ambil statistik dashboard"""
        try:
            stats = self.dashboard_repo.get_dashboard_stats()
            return stats
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in DashboardService.get_dashboard_stats: {str(e)}")
            raise  # Re-raise exception to be handled by controller
