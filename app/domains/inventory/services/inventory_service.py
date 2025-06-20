"""
Service untuk manajemen stok real-time
"""
import asyncio
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.domains.inventory.models.inventory_models import StockAlert, StockMovement, StockReservation

class StockMonitoringService:
    """Service untuk monitoring stok real-time"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def check_stock_levels(self, product_id: int, product_type: str, current_stock: int, min_stock: int):
        """Cek level stok dan buat alert jika perlu"""
        alert_level = self._determine_alert_level(current_stock, min_stock)
        
        if alert_level:
            self._create_stock_alert(product_id, product_type, current_stock, min_stock, alert_level)
    
    def _determine_alert_level(self, current_stock: int, min_stock: int) -> Optional[str]:
        """Tentukan level alert berdasarkan stok"""
        if current_stock == 0:
            return "empty"
        elif current_stock <= min_stock * 0.5:
            return "critical"
        elif current_stock <= min_stock:
            return "warning"
        return None
    
    def _create_stock_alert(self, product_id: int, product_type: str, current_stock: int, 
                           min_stock: int, alert_level: str):
        """Buat alert stok baru"""
        # Cek apakah sudah ada alert aktif untuk produk ini
        existing_alert = self.db.query(StockAlert).filter(
            StockAlert.product_id == product_id,
            StockAlert.product_type == product_type,
            StockAlert.is_resolved == False
        ).first()
        
        if not existing_alert:
            alert = StockAlert(
                product_id=product_id,
                product_type=product_type,
                current_stock=current_stock,
                min_stock=min_stock,
                alert_level=alert_level
            )
            self.db.add(alert)
            self.db.commit()
    
    def record_stock_movement(self, product_id: int, product_type: str, movement_type: str,
                            quantity: int, previous_stock: int, new_stock: int,
                            reference_id: str = None, notes: str = None, created_by: str = None):
        """Catat pergerakan stok"""
        movement = StockMovement(
            product_id=product_id,
            product_type=product_type,
            movement_type=movement_type,
            quantity=quantity,
            previous_stock=previous_stock,
            new_stock=new_stock,
            reference_id=reference_id,
            notes=notes,
            created_by=created_by
        )
        self.db.add(movement)
        self.db.commit()
        
        # Cek level stok setelah pergerakan
        if product_type == "game":
            # Ambil min_stock dari game_products (implementasi tergantung struktur DB)
            min_stock = 5  # Default, seharusnya dari database
            self.check_stock_levels(product_id, product_type, new_stock, min_stock)

class StockReservationService:
    """Service untuk reservasi stok sementara"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def reserve_stock(self, product_id: int, product_type: str, quantity: int, 
                     reserved_for: str, duration_minutes: int = 15) -> bool:
        """Reservasi stok untuk transaksi"""
        expires_at = datetime.utcnow() + timedelta(minutes=duration_minutes)
        
        reservation = StockReservation(
            product_id=product_id,
            product_type=product_type,
            quantity=quantity,
            reserved_for=reserved_for,
            expires_at=expires_at
        )
        
        self.db.add(reservation)
        self.db.commit()
        return True
    
    def release_reservation(self, reservation_id: int) -> bool:
        """Lepas reservasi stok"""
        reservation = self.db.query(StockReservation).filter(
            StockReservation.id == reservation_id
        ).first()
        
        if reservation and reservation.is_active:
            reservation.is_active = False
            reservation.released_at = datetime.utcnow()
            self.db.commit()
            return True
        return False
    
    def cleanup_expired_reservations(self):
        """Bersihkan reservasi yang sudah expired"""
        expired_reservations = self.db.query(StockReservation).filter(
            StockReservation.expires_at < datetime.utcnow(),
            StockReservation.is_active == True
        ).all()
        
        for reservation in expired_reservations:
            reservation.is_active = False
            reservation.released_at = datetime.utcnow()
        
        self.db.commit()
        return len(expired_reservations)
