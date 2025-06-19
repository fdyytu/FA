from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import datetime
from app.common.base_classes.base_repository import BaseRepository
from app.domains.voucher.models.voucher import Voucher, VoucherUsage, VoucherStatus

class VoucherRepository:
    """
    Repository untuk voucher - mengikuti SRP.
    Hanya menangani operasi database untuk voucher.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.model = Voucher
    
    def create(self, obj_data: dict) -> Voucher:
        """Buat voucher baru"""
        voucher = Voucher(**obj_data)
        self.db.add(voucher)
        self.db.commit()
        self.db.refresh(voucher)
        return voucher
    
    def get_by_id(self, voucher_id: int) -> Optional[Voucher]:
        """Ambil voucher berdasarkan ID"""
        return self.db.query(Voucher).filter(Voucher.id == voucher_id).first()
    
    def get_all(self) -> List[Voucher]:
        """Ambil semua voucher"""
        return self.db.query(Voucher).all()
    
    def update(self, voucher_id: int, update_data: dict) -> Voucher:
        """Update voucher"""
        voucher = self.get_by_id(voucher_id)
        if voucher:
            for key, value in update_data.items():
                setattr(voucher, key, value)
            self.db.commit()
            self.db.refresh(voucher)
        return voucher
    
    def get_by_code(self, code: str) -> Optional[Voucher]:
        """Ambil voucher berdasarkan kode"""
        return self.db.query(Voucher).filter(Voucher.code == code).first()
    
    def get_available_vouchers(self, user_id: int) -> List[Voucher]:
        """Ambil voucher yang tersedia untuk user"""
        now = datetime.now()
        return self.db.query(Voucher).filter(
            and_(
                Voucher.status == VoucherStatus.ACTIVE,
                Voucher.valid_from <= now,
                Voucher.valid_until >= now,
                func.coalesce(Voucher.usage_limit, 999999) > Voucher.usage_count
            )
        ).all()
    
    def get_user_usage_count(self, voucher_id: int, user_id: int) -> int:
        """Hitung berapa kali user sudah menggunakan voucher"""
        return self.db.query(VoucherUsage).filter(
            and_(
                VoucherUsage.voucher_id == voucher_id,
                VoucherUsage.user_id == user_id
            )
        ).count()
    
    def create_usage(self, usage_data: dict) -> VoucherUsage:
        """Buat record penggunaan voucher"""
        usage = VoucherUsage(**usage_data)
        self.db.add(usage)
        self.db.commit()
        self.db.refresh(usage)
        return usage
    
    def get_user_voucher_history(self, user_id: int, limit: int = 20) -> List[VoucherUsage]:
        """Ambil riwayat penggunaan voucher user"""
        return self.db.query(VoucherUsage).filter(
            VoucherUsage.user_id == user_id
        ).order_by(VoucherUsage.created_at.desc()).limit(limit).all()
    
    def get_voucher_stats(self) -> dict:
        """Ambil statistik voucher"""
        total = self.db.query(Voucher).count()
        active = self.db.query(Voucher).filter(Voucher.status == VoucherStatus.ACTIVE).count()
        expired = self.db.query(Voucher).filter(Voucher.status == VoucherStatus.EXPIRED).count()
        
        total_usage = self.db.query(VoucherUsage).count()
        total_discount = self.db.query(func.sum(VoucherUsage.discount_amount)).scalar() or 0
        
        return {
            "total_vouchers": total,
            "active_vouchers": active,
            "expired_vouchers": expired,
            "total_usage": total_usage,
            "total_discount_given": float(total_discount)
        }
    
    def expire_old_vouchers(self) -> int:
        """Expire voucher yang sudah kadaluarsa"""
        now = datetime.now()
        updated = self.db.query(Voucher).filter(
            and_(
                Voucher.valid_until < now,
                Voucher.status == VoucherStatus.ACTIVE
            )
        ).update({"status": VoucherStatus.EXPIRED}, synchronize_session=False)
        self.db.commit()
        return updated
