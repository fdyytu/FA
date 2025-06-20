"""
Service untuk keamanan dan anti-fraud
"""
import hashlib
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from collections import defaultdict

class AntiFraudService:
    """Service untuk deteksi fraud dan keamanan"""
    
    def __init__(self, db: Session):
        self.db = db
        self.suspicious_patterns = {
            "rapid_transactions": 5,  # Max 5 transaksi dalam 1 menit
            "daily_limit": 10,        # Max 10 transaksi per hari untuk user baru
            "amount_threshold": 1000000,  # Transaksi di atas 1 juta perlu verifikasi
        }
        self.blacklisted_ips = set()
        self.blacklisted_users = set()
    
    def check_transaction_fraud(self, user_id: str, amount: float, ip_address: str) -> Dict:
        """Cek apakah transaksi mencurigakan"""
        fraud_score = 0
        reasons = []
        
        # Cek IP blacklist
        if ip_address in self.blacklisted_ips:
            return {
                "is_fraud": True,
                "score": 100,
                "reasons": ["IP address dalam blacklist"],
                "action": "block"
            }
        
        # Cek user blacklist
        if user_id in self.blacklisted_users:
            return {
                "is_fraud": True,
                "score": 100,
                "reasons": ["User dalam blacklist"],
                "action": "block"
            }
        
        # Cek rapid transactions
        rapid_check = self._check_rapid_transactions(user_id)
        if rapid_check["is_suspicious"]:
            fraud_score += 30
            reasons.append("Transaksi terlalu cepat")
        
        # Cek daily limit
        daily_check = self._check_daily_limit(user_id)
        if daily_check["is_suspicious"]:
            fraud_score += 20
            reasons.append("Melebihi batas harian")
        
        # Cek amount threshold
        if amount > self.suspicious_patterns["amount_threshold"]:
            fraud_score += 25
            reasons.append("Nominal transaksi tinggi")
        
        # Cek pattern anomali
        pattern_check = self._check_user_pattern(user_id, amount)
        if pattern_check["is_suspicious"]:
            fraud_score += 15
            reasons.append("Pola transaksi tidak biasa")
        
        # Tentukan action berdasarkan score
        action = "allow"
        if fraud_score >= 70:
            action = "block"
        elif fraud_score >= 40:
            action = "review"
        elif fraud_score >= 20:
            action = "verify"
        
        return {
            "is_fraud": fraud_score >= 40,
            "score": fraud_score,
            "reasons": reasons,
            "action": action
        }
    
    def _check_rapid_transactions(self, user_id: str) -> Dict:
        """Cek transaksi rapid dalam 1 menit terakhir"""
        # Simulasi pengecekan (implementasi nyata perlu query database)
        # Anggap ada 3 transaksi dalam 1 menit terakhir
        recent_count = 3
        
        return {
            "is_suspicious": recent_count >= self.suspicious_patterns["rapid_transactions"],
            "count": recent_count,
            "limit": self.suspicious_patterns["rapid_transactions"]
        }
    
    def _check_daily_limit(self, user_id: str) -> Dict:
        """Cek batas transaksi harian"""
        # Simulasi pengecekan
        daily_count = 8
        
        return {
            "is_suspicious": daily_count >= self.suspicious_patterns["daily_limit"],
            "count": daily_count,
            "limit": self.suspicious_patterns["daily_limit"]
        }
    
    def _check_user_pattern(self, user_id: str, amount: float) -> Dict:
        """Cek pola transaksi user"""
        # Simulasi analisis pola
        # Misalnya user biasanya transaksi 50rb, tiba-tiba 500rb
        avg_amount = 50000
        deviation = abs(amount - avg_amount) / avg_amount
        
        return {
            "is_suspicious": deviation > 5.0,  # 500% dari rata-rata
            "deviation": deviation,
            "average": avg_amount
        }
    
    def add_to_blacklist(self, identifier: str, type_: str) -> bool:
        """Tambah ke blacklist"""
        if type_ == "ip":
            self.blacklisted_ips.add(identifier)
        elif type_ == "user":
            self.blacklisted_users.add(identifier)
        return True
    
    def remove_from_blacklist(self, identifier: str, type_: str) -> bool:
        """Hapus dari blacklist"""
        if type_ == "ip" and identifier in self.blacklisted_ips:
            self.blacklisted_ips.remove(identifier)
        elif type_ == "user" and identifier in self.blacklisted_users:
            self.blacklisted_users.remove(identifier)
        return True

class AuditTrailService:
    """Service untuk audit trail dan logging"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def log_user_activity(self, user_id: str, action: str, details: Dict, ip_address: str = None):
        """Log aktivitas user"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "action": action,
            "details": details,
            "ip_address": ip_address,
            "session_id": self._generate_session_id(user_id)
        }
        
        # Dalam implementasi nyata, simpan ke database atau file log
        print(f"AUDIT LOG: {json.dumps(log_entry)}")
    
    def log_transaction(self, transaction_id: str, user_id: str, amount: float, 
                       status: str, payment_method: str):
        """Log transaksi"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": "transaction",
            "transaction_id": transaction_id,
            "user_id": user_id,
            "amount": amount,
            "status": status,
            "payment_method": payment_method
        }
        
        print(f"TRANSACTION LOG: {json.dumps(log_entry)}")
    
    def _generate_session_id(self, user_id: str) -> str:
        """Generate session ID"""
        timestamp = str(datetime.utcnow().timestamp())
        return hashlib.md5(f"{user_id}_{timestamp}".encode()).hexdigest()[:16]
