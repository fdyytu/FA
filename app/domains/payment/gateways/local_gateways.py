"""
Payment Gateway untuk layanan pembayaran lokal Indonesia
"""
import asyncio
import aiohttp
import json
from typing import Dict, Optional
from datetime import datetime, timedelta
from abc import ABC, abstractmethod

class BasePaymentGateway(ABC):
    """Base class untuk payment gateway"""
    
    @abstractmethod
    async def create_payment(self, amount: float, order_id: str, customer_info: Dict) -> Dict:
        pass
    
    @abstractmethod
    async def check_payment_status(self, payment_id: str) -> Dict:
        pass

class DANAGateway(BasePaymentGateway):
    """Payment Gateway untuk DANA"""
    
    def __init__(self, merchant_id: str, api_key: str, sandbox: bool = True):
        self.merchant_id = merchant_id
        self.api_key = api_key
        self.base_url = "https://sandbox-api.dana.id" if sandbox else "https://api.dana.id"
    
    async def create_payment(self, amount: float, order_id: str, customer_info: Dict) -> Dict:
        """Buat pembayaran DANA"""
        try:
            payload = {
                "merchantId": self.merchant_id,
                "orderId": order_id,
                "amount": int(amount),
                "currency": "IDR",
                "customerInfo": customer_info,
                "expiredTime": (datetime.now() + timedelta(hours=1)).isoformat()
            }
            
            # Simulasi response DANA (implementasi sebenarnya perlu API DANA)
            return {
                "success": True,
                "payment_id": f"dana_{order_id}",
                "payment_url": f"https://m.dana.id/pay/{order_id}",
                "qr_code": f"data:image/png;base64,iVBORw0KGgoAAAANS...",
                "expired_time": payload["expiredTime"],
                "status": "pending"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def check_payment_status(self, payment_id: str) -> Dict:
        """Cek status pembayaran DANA"""
        # Simulasi pengecekan status
        return {
            "payment_id": payment_id,
            "status": "pending",  # pending, success, failed, expired
            "amount": 50000,
            "paid_at": None
        }

class OVOGateway(BasePaymentGateway):
    """Payment Gateway untuk OVO"""
    
    def __init__(self, merchant_id: str, api_key: str, sandbox: bool = True):
        self.merchant_id = merchant_id
        self.api_key = api_key
        self.base_url = "https://sandbox-api.ovo.id" if sandbox else "https://api.ovo.id"
    
    async def create_payment(self, amount: float, order_id: str, customer_info: Dict) -> Dict:
        """Buat pembayaran OVO"""
        try:
            payload = {
                "merchantId": self.merchant_id,
                "orderId": order_id,
                "amount": int(amount),
                "currency": "IDR",
                "customerPhone": customer_info.get("phone"),
                "description": f"Topup game - {order_id}"
            }
            
            # Simulasi response OVO
            return {
                "success": True,
                "payment_id": f"ovo_{order_id}",
                "payment_url": f"https://pay.ovo.id/{order_id}",
                "push_notification_sent": True,
                "status": "pending"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def check_payment_status(self, payment_id: str) -> Dict:
        """Cek status pembayaran OVO"""
        return {
            "payment_id": payment_id,
            "status": "pending",
            "amount": 50000,
            "paid_at": None
        }

class GopayGateway(BasePaymentGateway):
    """Payment Gateway untuk GoPay"""
    
    def __init__(self, merchant_id: str, api_key: str, sandbox: bool = True):
        self.merchant_id = merchant_id
        self.api_key = api_key
        self.base_url = "https://sandbox-api.gopay.co.id" if sandbox else "https://api.gopay.co.id"
    
    async def create_payment(self, amount: float, order_id: str, customer_info: Dict) -> Dict:
        """Buat pembayaran GoPay"""
        try:
            payload = {
                "merchantId": self.merchant_id,
                "orderId": order_id,
                "amount": int(amount),
                "currency": "IDR",
                "customerEmail": customer_info.get("email"),
                "description": f"Game topup - {order_id}"
            }
            
            # Simulasi response GoPay
            return {
                "success": True,
                "payment_id": f"gopay_{order_id}",
                "qr_code_url": f"https://api.gopay.co.id/qr/{order_id}",
                "deeplink_url": f"gojek://gopay/pay/{order_id}",
                "status": "pending"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def check_payment_status(self, payment_id: str) -> Dict:
        """Cek status pembayaran GoPay"""
        return {
            "payment_id": payment_id,
            "status": "pending",
            "amount": 50000,
            "paid_at": None
        }
