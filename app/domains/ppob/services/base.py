from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from app.schemas.ppob import PPOBInquiryResponse, PPOBInquiryRequest
from app.domains.ppob.models.ppob import PPOBCategory

class PPOBProviderInterface(ABC):
    """Interface untuk PPOB Provider (Interface Segregation Principle)"""
    
    @abstractmethod
    async def inquiry(self, request: PPOBInquiryRequest) -> PPOBInquiryResponse:
        """Melakukan inquiry tagihan"""
        pass
    
    @abstractmethod
    async def payment(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Melakukan pembayaran"""
        pass
    
    @abstractmethod
    def get_supported_categories(self) -> list[PPOBCategory]:
        """Mendapatkan kategori yang didukung"""
        pass

class BasePPOBProvider(PPOBProviderInterface):
    """Base class untuk PPOB Provider (Open/Closed Principle)"""
    
    def __init__(self, api_url: str, api_key: str, timeout: int = 30):
        self.api_url = api_url
        self.api_key = api_key
        self.timeout = timeout
    
    def _get_headers(self) -> Dict[str, str]:
        """Header untuk API request"""
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
    
    def _generate_transaction_code(self) -> str:
        """Generate unique transaction code"""
        import uuid
        import datetime
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        unique_id = str(uuid.uuid4())[:8].upper()
        return f"TRX{timestamp}{unique_id}"
    
    async def _make_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Helper method untuk membuat HTTP request"""
        import aiohttp
        import asyncio
        
        url = f"{self.api_url}/{endpoint}"
        headers = self._get_headers()
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                async with session.post(url, json=data, headers=headers) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        raise Exception(f"API Error: {response.status} - {await response.text()}")
        except asyncio.TimeoutError:
            raise Exception("Request timeout")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")
