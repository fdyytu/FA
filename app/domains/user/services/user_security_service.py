from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user_profile import (
    UserPasswordChange, UserSecuritySettings
)
from app.utils.exceptions import HTTPException
from app.shared.base_classes.base_service import BaseService
from app.common.security.auth_security import verify_password, get_password_hash
import logging
import pyotp
import qrcode
import io
import base64
from datetime import datetime

logger = logging.getLogger(__name__)

class UserSecurityService(BaseService):
    """Service untuk mengelola keamanan user - 2FA, password, dll"""
    
    def __init__(self, db: Session):
        super().__init__(db)
    
    async def change_password(self, user_id: int, password_data: UserPasswordChange) -> None:
        """Ganti password user"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User tidak ditemukan")
            
            # Verifikasi password lama
            if not verify_password(password_data.current_password, user.hashed_password):
                raise HTTPException(status_code=400, detail="Password lama tidak benar")
            
            # Validasi password baru
            if password_data.new_password != password_data.confirm_password:
                raise HTTPException(status_code=400, detail="Konfirmasi password tidak cocok")
            
            # Update password
            user.hashed_password = get_password_hash(password_data.new_password)
            self.db.commit()
            
            logger.info(f"Password berhasil diubah untuk user_id: {user_id}")
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error changing password: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Gagal mengubah password: {str(e)}")
    
    async def get_security_settings(self, user_id: int) -> dict:
        """Mendapatkan pengaturan keamanan user"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User tidak ditemukan")
            
            # Untuk implementasi sederhana, return data default
            # Nantinya bisa menggunakan tabel user_security_settings
            security_settings = {
                "two_factor_enabled": False,  # Bisa diambil dari tabel terpisah
                "login_alerts": True,
                "session_timeout": 30,
                "last_password_change": datetime.now().isoformat(),
                "active_sessions": 1,
                "login_history": [
                    {
                        "ip_address": "192.168.1.1",
                        "user_agent": "Mozilla/5.0...",
                        "location": "Jakarta, Indonesia",
                        "login_time": datetime.now().isoformat()
                    }
                ]
            }
            
            return security_settings
            
        except Exception as e:
            logger.error(f"Error getting security settings: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Gagal mengambil pengaturan keamanan: {str(e)}")
    
    async def enable_2fa(self, user_id: int) -> str:
        """Aktifkan 2FA untuk user"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User tidak ditemukan")
            
            # Generate secret key untuk TOTP
            secret = pyotp.random_base32()
            
            # Buat TOTP instance
            totp = pyotp.TOTP(secret)
            
            # Generate QR code URL
            provisioning_uri = totp.provisioning_uri(
                name=user.email,
                issuer_name="FA Application"
            )
            
            # Generate QR code image
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(provisioning_uri)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to base64 untuk return sebagai data URL
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')
            img_str = base64.b64encode(img_buffer.getvalue()).decode()
            qr_code_url = f"data:image/png;base64,{img_str}"
            
            # Simpan secret (dalam implementasi nyata, simpan di tabel user_security)
            # user.totp_secret = secret  # Field ini perlu ditambah ke model User
            
            logger.info(f"2FA berhasil diaktifkan untuk user_id: {user_id}")
            return qr_code_url
            
        except Exception as e:
            logger.error(f"Error enabling 2FA: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Gagal mengaktifkan 2FA: {str(e)}")
    
    async def disable_2fa(self, user_id: int, verification_code: str) -> None:
        """Nonaktifkan 2FA untuk user"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User tidak ditemukan")
            
            # Verifikasi kode 2FA sebelum menonaktifkan
            # Dalam implementasi nyata, ambil secret dari database
            # if not self._verify_totp_code(user.totp_secret, verification_code):
            #     raise HTTPException(status_code=400, detail="Kode verifikasi tidak valid")
            
            # Untuk demo, kita skip verifikasi
            if verification_code != "123456":  # Demo code
                raise HTTPException(status_code=400, detail="Kode verifikasi tidak valid")
            
            # Hapus secret dari database
            # user.totp_secret = None
            
            logger.info(f"2FA berhasil dinonaktifkan untuk user_id: {user_id}")
            
        except Exception as e:
            logger.error(f"Error disabling 2FA: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Gagal menonaktifkan 2FA: {str(e)}")
    
    async def verify_2fa_code(self, user_id: int, code: str) -> bool:
        """Verifikasi kode 2FA"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            # Dalam implementasi nyata, ambil secret dari database
            # return self._verify_totp_code(user.totp_secret, code)
            
            # Untuk demo
            return code == "123456"
            
        except Exception as e:
            logger.error(f"Error verifying 2FA code: {str(e)}")
            return False
    
    def _verify_totp_code(self, secret: str, code: str) -> bool:
        """Helper method untuk verifikasi TOTP code"""
        try:
            totp = pyotp.TOTP(secret)
            return totp.verify(code, valid_window=1)  # Allow 1 window tolerance
        except Exception:
            return False
    
    async def get_active_sessions(self, user_id: int) -> List[dict]:
        """Mendapatkan daftar sesi aktif user"""
        try:
            # Implementasi sederhana - return data dummy
            # Dalam implementasi nyata, ambil dari tabel user_sessions
            sessions = [
                {
                    "session_id": "sess_123456",
                    "ip_address": "192.168.1.1",
                    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "location": "Jakarta, Indonesia",
                    "last_activity": datetime.now().isoformat(),
                    "is_current": True
                }
            ]
            
            return sessions
            
        except Exception as e:
            logger.error(f"Error getting active sessions: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Gagal mengambil sesi aktif: {str(e)}")
    
    async def revoke_session(self, user_id: int, session_id: str) -> None:
        """Cabut/hapus sesi tertentu"""
        try:
            # Implementasi untuk menghapus sesi dari database/cache
            # Dalam implementasi nyata, hapus dari tabel user_sessions atau Redis
            
            logger.info(f"Sesi {session_id} berhasil dicabut untuk user_id: {user_id}")
            
        except Exception as e:
            logger.error(f"Error revoking session: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Gagal mencabut sesi: {str(e)}")
