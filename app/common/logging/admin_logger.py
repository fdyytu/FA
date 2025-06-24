"""
Sistem logging untuk domain admin
Menyediakan logging detail untuk error dan aktivitas admin
"""

import logging
import sys
from datetime import datetime
from typing import Optional, Dict, Any
import traceback
import json

class AdminLogger:
    """Logger khusus untuk domain admin dengan detail error"""
    
    def __init__(self, name: str = "admin_domain"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Hapus handler yang sudah ada untuk menghindari duplikasi
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        # Console handler dengan format detail
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Format yang detail untuk debugging
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    def info(self, message: str, extra_data: Optional[Dict[str, Any]] = None):
        """Log info dengan data tambahan"""
        if extra_data:
            message = f"{message} | Data: {json.dumps(extra_data, default=str)}"
        self.logger.info(message)
    
    def error(self, message: str, error: Optional[Exception] = None, extra_data: Optional[Dict[str, Any]] = None):
        """Log error dengan detail lengkap"""
        error_details = {
            "timestamp": datetime.utcnow().isoformat(),
            "message": message,
        }
        
        if error:
            error_details.update({
                "error_type": type(error).__name__,
                "error_message": str(error),
                "traceback": traceback.format_exc()
            })
        
        if extra_data:
            error_details["extra_data"] = extra_data
        
        self.logger.error(f"ERROR DETAIL: {json.dumps(error_details, indent=2, default=str)}")
    
    def warning(self, message: str, extra_data: Optional[Dict[str, Any]] = None):
        """Log warning dengan data tambahan"""
        if extra_data:
            message = f"{message} | Data: {json.dumps(extra_data, default=str)}"
        self.logger.warning(message)
    
    def debug(self, message: str, extra_data: Optional[Dict[str, Any]] = None):
        """Log debug dengan data tambahan"""
        if extra_data:
            message = f"{message} | Data: {json.dumps(extra_data, default=str)}"
        self.logger.debug(message)

# Instance global untuk digunakan di seluruh domain admin
admin_logger = AdminLogger()
