from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional, Dict, Any
from decimal import Decimal
import base64
from cryptography.fernet import Fernet
from app.models.admin import AdminConfig, PPOBMarginConfig, MarginType
from app.schemas.admin import (
    AdminConfigCreate, AdminConfigUpdate, PPOBMarginConfigCreate, 
    PPOBMarginConfigUpdate, DigiflazzConfigRequest
)
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class AdminConfigService:
    """Service untuk mengelola konfigurasi admin"""
    
    def __init__(self, db: Session):
        self.db = db
        self._encryption_key = self._get_or_create_encryption_key()
    
    def _get_or_create_encryption_key(self) -> bytes:
        """Ambil atau buat encryption key untuk enkripsi data sensitif"""
        try:
            # Coba ambil key dari database
            key_config = self.db.query(AdminConfig).filter(
                AdminConfig.config_key == "encryption_key"
            ).first()
            
            if key_config:
                return base64.b64decode(key_config.config_value.encode())
            else:
                # Buat key baru
                key = Fernet.generate_key()
                key_config = AdminConfig(
                    config_key="encryption_key",
                    config_value=base64.b64encode(key).decode(),
                    config_type="encrypted",
                    description="Encryption key untuk data sensitif"
                )
                self.db.add(key_config)
                self.db.commit()
                return key
        except Exception as e:
            logger.error(f"Error managing encryption key: {str(e)}")
            # Fallback ke key dari settings
            return settings.SECRET_KEY.encode()[:32].ljust(32, b'0')
    
    def _encrypt_value(self, value: str) -> str:
        """Enkripsi nilai sensitif"""
        try:
            f = Fernet(self._encryption_key)
            return f.encrypt(value.encode()).decode()
        except Exception as e:
            logger.error(f"Encryption error: {str(e)}")
            return value
    
    def _decrypt_value(self, encrypted_value: str) -> str:
        """Dekripsi nilai sensitif"""
        try:
            f = Fernet(self._encryption_key)
            return f.decrypt(encrypted_value.encode()).decode()
        except Exception as e:
            logger.error(f"Decryption error: {str(e)}")
            return encrypted_value
    
    def create_config(self, config_data: AdminConfigCreate) -> AdminConfig:
        """Buat konfigurasi baru"""
        try:
            # Cek apakah config sudah ada
            existing = self.db.query(AdminConfig).filter(
                AdminConfig.config_key == config_data.config_key
            ).first()
            
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Konfigurasi dengan key '{config_data.config_key}' sudah ada"
                )
            
            # Enkripsi jika tipe encrypted
            config_value = config_data.config_value
            if config_data.config_type == "encrypted":
                config_value = self._encrypt_value(config_data.config_value)
            
            config = AdminConfig(
                config_key=config_data.config_key,
                config_value=config_value,
                config_type=config_data.config_type,
                description=config_data.description,
                is_active=config_data.is_active
            )
            
            self.db.add(config)
            self.db.commit()
            self.db.refresh(config)
            
            logger.info(f"Created admin config: {config_data.config_key}")
            return config
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal membuat konfigurasi: {str(e)}"
            )
    
    def get_config(self, config_key: str, decrypt: bool = True) -> Optional[AdminConfig]:
        """Ambil konfigurasi berdasarkan key"""
        config = self.db.query(AdminConfig).filter(
            AdminConfig.config_key == config_key,
            AdminConfig.is_active == True
        ).first()
        
        if config and config.config_type == "encrypted" and decrypt:
            # Buat copy untuk tidak mengubah object asli
            decrypted_config = AdminConfig(
                id=config.id,
                config_key=config.config_key,
                config_value=self._decrypt_value(config.config_value),
                config_type=config.config_type,
                description=config.description,
                is_active=config.is_active,
                created_at=config.created_at,
                updated_at=config.updated_at
            )
            return decrypted_config
        
        return config
    
    def update_config(self, config_key: str, update_data: AdminConfigUpdate) -> AdminConfig:
        """Update konfigurasi"""
        try:
            config = self.db.query(AdminConfig).filter(
                AdminConfig.config_key == config_key
            ).first()
            
            if not config:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Konfigurasi tidak ditemukan"
                )
            
            # Update fields yang diberikan
            if update_data.config_value is not None:
                if config.config_type == "encrypted":
                    config.config_value = self._encrypt_value(update_data.config_value)
                else:
                    config.config_value = update_data.config_value
            
            if update_data.config_type is not None:
                config.config_type = update_data.config_type
            
            if update_data.description is not None:
                config.description = update_data.description
            
            if update_data.is_active is not None:
                config.is_active = update_data.is_active
            
            self.db.commit()
            self.db.refresh(config)
            
            logger.info(f"Updated admin config: {config_key}")
            return config
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal update konfigurasi: {str(e)}"
            )
    
    def delete_config(self, config_key: str) -> bool:
        """Hapus konfigurasi"""
        try:
            config = self.db.query(AdminConfig).filter(
                AdminConfig.config_key == config_key
            ).first()
            
            if not config:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Konfigurasi tidak ditemukan"
                )
            
            self.db.delete(config)
            self.db.commit()
            
            logger.info(f"Deleted admin config: {config_key}")
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal hapus konfigurasi: {str(e)}"
            )
    
    def get_all_configs(self, include_encrypted: bool = False) -> List[AdminConfig]:
        """Ambil semua konfigurasi"""
        configs = self.db.query(AdminConfig).filter(
            AdminConfig.is_active == True
        ).all()
        
        if not include_encrypted:
            # Filter out encrypted configs atau mask valuenya
            filtered_configs = []
            for config in configs:
                if config.config_type == "encrypted":
                    # Mask encrypted values
                    masked_config = AdminConfig(
                        id=config.id,
                        config_key=config.config_key,
                        config_value="***ENCRYPTED***",
                        config_type=config.config_type,
                        description=config.description,
                        is_active=config.is_active,
                        created_at=config.created_at,
                        updated_at=config.updated_at
                    )
                    filtered_configs.append(masked_config)
                else:
                    filtered_configs.append(config)
            return filtered_configs
        
        return configs
    
    def set_digiflazz_config(self, config_data: DigiflazzConfigRequest) -> Dict[str, Any]:
        """Set konfigurasi Digiflazz"""
        try:
            # Set username
            username_config = self.get_config("digiflazz_username")
            if username_config:
                self.update_config("digiflazz_username", AdminConfigUpdate(
                    config_value=config_data.username
                ))
            else:
                self.create_config(AdminConfigCreate(
                    config_key="digiflazz_username",
                    config_value=config_data.username,
                    config_type="string",
                    description="Username Digiflazz"
                ))
            
            # Set API key (encrypted)
            api_key_config = self.get_config("digiflazz_api_key")
            if api_key_config:
                self.update_config("digiflazz_api_key", AdminConfigUpdate(
                    config_value=config_data.api_key
                ))
            else:
                self.create_config(AdminConfigCreate(
                    config_key="digiflazz_api_key",
                    config_value=config_data.api_key,
                    config_type="encrypted",
                    description="API Key Digiflazz"
                ))
            
            # Set production mode
            production_config = self.get_config("digiflazz_production")
            if production_config:
                self.update_config("digiflazz_production", AdminConfigUpdate(
                    config_value=str(config_data.production)
                ))
            else:
                self.create_config(AdminConfigCreate(
                    config_key="digiflazz_production",
                    config_value=str(config_data.production),
                    config_type="boolean",
                    description="Mode production Digiflazz"
                ))
            
            logger.info("Digiflazz configuration updated successfully")
            return {
                "message": "Konfigurasi Digiflazz berhasil disimpan",
                "username": config_data.username,
                "production": config_data.production
            }
            
        except Exception as e:
            logger.error(f"Error setting Digiflazz config: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal menyimpan konfigurasi Digiflazz: {str(e)}"
            )
    
    def get_digiflazz_config(self) -> Dict[str, Any]:
        """Ambil konfigurasi Digiflazz"""
        try:
            username_config = self.get_config("digiflazz_username")
            api_key_config = self.get_config("digiflazz_api_key")
            production_config = self.get_config("digiflazz_production")
            
            return {
                "username": username_config.config_value if username_config else "",
                "api_key": api_key_config.config_value if api_key_config else "",
                "production": production_config.config_value.lower() == "true" if production_config else False,
                "is_configured": bool(username_config and api_key_config)
            }
            
        except Exception as e:
            logger.error(f"Error getting Digiflazz config: {str(e)}")
            return {
                "username": "",
                "api_key": "",
                "production": False,
                "is_configured": False
            }

class PPOBMarginService:
    """Service untuk mengelola margin PPOB"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_margin_config(self, margin_data: PPOBMarginConfigCreate) -> PPOBMarginConfig:
        """Buat konfigurasi margin baru"""
        try:
            # Cek apakah sudah ada config untuk kategori/produk yang sama
            existing = self.db.query(PPOBMarginConfig).filter(
                PPOBMarginConfig.category == margin_data.category,
                PPOBMarginConfig.product_code == margin_data.product_code,
                PPOBMarginConfig.is_active == True
            ).first()
            
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Konfigurasi margin untuk kategori/produk ini sudah ada"
                )
            
            margin_config = PPOBMarginConfig(**margin_data.dict())
            self.db.add(margin_config)
            self.db.commit()
            self.db.refresh(margin_config)
            
            logger.info(f"Created margin config for {margin_data.category}")
            return margin_config
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal membuat konfigurasi margin: {str(e)}"
            )
    
    def get_margin_config(self, category: str, product_code: Optional[str] = None) -> Optional[PPOBMarginConfig]:
        """Ambil konfigurasi margin"""
        # Cari margin spesifik produk dulu
        if product_code:
            margin = self.db.query(PPOBMarginConfig).filter(
                PPOBMarginConfig.category == category,
                PPOBMarginConfig.product_code == product_code,
                PPOBMarginConfig.is_active == True
            ).first()
            
            if margin:
                return margin
        
        # Jika tidak ada, cari margin kategori
        margin = self.db.query(PPOBMarginConfig).filter(
            PPOBMarginConfig.category == category,
            PPOBMarginConfig.product_code.is_(None),
            PPOBMarginConfig.is_active == True
        ).first()
        
        if margin:
            return margin
        
        # Jika tidak ada, cari margin global
        return self.db.query(PPOBMarginConfig).filter(
            PPOBMarginConfig.category == "global",
            PPOBMarginConfig.product_code.is_(None),
            PPOBMarginConfig.is_active == True
        ).first()
    
    def calculate_price_with_margin(self, base_price: Decimal, category: str, product_code: Optional[str] = None) -> Decimal:
        """Hitung harga dengan margin"""
        margin_config = self.get_margin_config(category, product_code)
        
        if not margin_config:
            return base_price
        
        if margin_config.margin_type == MarginType.PERCENTAGE:
            margin_amount = base_price * (margin_config.margin_value / 100)
        else:  # NOMINAL
            margin_amount = margin_config.margin_value
        
        return base_price + margin_amount
    
    def update_margin_config(self, margin_id: int, update_data: PPOBMarginConfigUpdate) -> PPOBMarginConfig:
        """Update konfigurasi margin"""
        try:
            margin = self.db.query(PPOBMarginConfig).filter(
                PPOBMarginConfig.id == margin_id
            ).first()
            
            if not margin:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Konfigurasi margin tidak ditemukan"
                )
            
            # Update fields yang diberikan
            for field, value in update_data.dict(exclude_unset=True).items():
                setattr(margin, field, value)
            
            self.db.commit()
            self.db.refresh(margin)
            
            logger.info(f"Updated margin config ID: {margin_id}")
            return margin
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal update konfigurasi margin: {str(e)}"
            )
    
    def delete_margin_config(self, margin_id: int) -> bool:
        """Hapus konfigurasi margin"""
        try:
            margin = self.db.query(PPOBMarginConfig).filter(
                PPOBMarginConfig.id == margin_id
            ).first()
            
            if not margin:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Konfigurasi margin tidak ditemukan"
                )
            
            self.db.delete(margin)
            self.db.commit()
            
            logger.info(f"Deleted margin config ID: {margin_id}")
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal hapus konfigurasi margin: {str(e)}"
            )
    
    def get_all_margin_configs(self) -> List[PPOBMarginConfig]:
        """Ambil semua konfigurasi margin"""
        return self.db.query(PPOBMarginConfig).filter(
            PPOBMarginConfig.is_active == True
        ).all()
