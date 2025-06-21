# Audit Logging Core Service untuk Discord Admin Actions
from datetime import datetime
from typing import Optional, Dict, Any
import json
import logging

# Setup logger
audit_logger = logging.getLogger("discord_audit")
audit_logger.setLevel(logging.INFO)

class AuditLogger:
    def __init__(self):
        self.logger = audit_logger
    
    def log_admin_action(self, 
                        user_id: str, 
                        action: str, 
                        resource: str,
                        details: Optional[Dict[str, Any]] = None,
                        ip_address: Optional[str] = None):
        """Log admin action ke database dan file"""
        timestamp = datetime.utcnow()
        
        audit_entry = {
            "timestamp": timestamp.isoformat(),
            "user_id": user_id,
            "action": action,
            "resource": resource,
            "details": details or {},
            "ip_address": ip_address,
            "severity": self._get_severity(action)
        }
        
        # Log ke file
        self.logger.info(f"AUDIT: {json.dumps(audit_entry)}")
        
        # TODO: Simpan ke database audit_logs table
        return audit_entry
    
    def _get_severity(self, action: str) -> str:
        """Tentukan severity berdasarkan action"""
        high_risk_actions = ["delete", "stop_all", "bulk_delete"]
        medium_risk_actions = ["update", "restart", "bulk_update"]
        
        if any(risk in action.lower() for risk in high_risk_actions):
            return "HIGH"
        elif any(risk in action.lower() for risk in medium_risk_actions):
            return "MEDIUM"
        return "LOW"

# Instance global
audit_logger_service = AuditLogger()
