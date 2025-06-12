from typing import Dict, Any
from app.services.ppob.base import BasePPOBProvider
from app.schemas.ppob import PPOBInquiryResponse, PPOBInquiryRequest
from app.models.ppob import PPOBCategory
import asyncio

class DefaultPPOBProvider(BasePPOBProvider):
    """Implementasi PPOB Provider Default"""
    
    async def inquiry(self, request: PPOBInquiryRequest) -> PPOBInquiryResponse:
        """Simulasi inquiry tagihan"""
        await asyncio.sleep(1)  # Simulasi delay
        
        # Simulasi data inquiry
        inquiry_data = {
            "customer_number": request.customer_number,
            "customer_name": "Pelanggan Default",
            "amount": 50000,
            "admin_fee": 2500,
            "total_amount": 52500,
            "product_name": "Pulsa 50K",
            "ref_id": self._generate_transaction_code()
        }
        
        return PPOBInquiryResponse(**inquiry_data)
    
    async def payment(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Simulasi pembayaran"""
        await asyncio.sleep(1)  # Simulasi delay
        
        # Simulasi data pembayaran
        payment_data = {
            "transaction_id": self._generate_transaction_code(),
            "status": "success",
            "message": "Pembayaran berhasil"
        }
        
        return payment_data
    
    def get_supported_categories(self) -> list[PPOBCategory]:
        """Kategori yang didukung"""
        return [PPOBCategory.PULSA, PPOBCategory.LISTRIK, PPOBCategory.PDAM]
