import aiohttp
import asyncio
from typing import Dict, Any, List
from app.services.ppob.base import BasePPOBProvider
from app.schemas.ppob import PPOBInquiryResponse, PPOBInquiryRequest
from app.models.ppob import PPOBCategory
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class DigiflazzProvider(BasePPOBProvider):
    """Implementasi PPOB Provider untuk Digiflazz"""
    
    def __init__(self, username: str, api_key: str, production: bool = False):
        # Digiflazz menggunakan username dan api_key, bukan URL
        self.username = username
        self.api_key = api_key
        self.production = production
        self.base_url = "https://api.digiflazz.com/v1" if production else "https://api.digiflazz.com/v1"
        self.timeout = 30
        
        logger.info(f"DigiflazzProvider initialized - Production: {production}")
    
    def _get_headers(self) -> Dict[str, str]:
        """Header untuk API request Digiflazz"""
        return {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def _create_signature(self, data: Dict[str, Any]) -> str:
        """Buat signature untuk Digiflazz API"""
        import hashlib
        import json
        
        # Digiflazz menggunakan MD5 hash dari username + api_key + ref_id
        ref_id = data.get('ref_id', '')
        raw_signature = self.username + self.api_key + ref_id
        return hashlib.md5(raw_signature.encode()).hexdigest()
    
    async def inquiry(self, request: PPOBInquiryRequest) -> PPOBInquiryResponse:
        """Melakukan inquiry tagihan melalui Digiflazz"""
        try:
            ref_id = self._generate_transaction_code()
            
            # Format data untuk Digiflazz
            inquiry_data = {
                "username": self.username,
                "buyer_sku_code": request.product_code,
                "customer_no": request.customer_number,
                "ref_id": ref_id,
                "sign": ""
            }
            
            # Buat signature
            inquiry_data["sign"] = self._create_signature(inquiry_data)
            
            logger.info(f"Digiflazz inquiry request: {inquiry_data}")
            
            # Panggil API Digiflazz
            response = await self._make_digiflazz_request("transaction", inquiry_data)
            
            # Parse response Digiflazz
            if response.get("data", {}).get("status") == "Gagal":
                raise Exception(f"Inquiry gagal: {response.get('data', {}).get('message', 'Unknown error')}")
            
            # Format response sesuai schema aplikasi
            inquiry_response = PPOBInquiryResponse(
                customer_number=request.customer_number,
                customer_name=response.get("data", {}).get("customer_name", ""),
                amount=float(response.get("data", {}).get("price", 0)),
                admin_fee=float(response.get("data", {}).get("admin_fee", 0)),
                total_amount=float(response.get("data", {}).get("price", 0)) + float(response.get("data", {}).get("admin_fee", 0)),
                product_name=response.get("data", {}).get("product_name", ""),
                ref_id=ref_id
            )
            
            logger.info(f"Digiflazz inquiry success: {inquiry_response}")
            return inquiry_response
            
        except Exception as e:
            logger.error(f"Digiflazz inquiry error: {str(e)}")
            raise Exception(f"Gagal melakukan inquiry: {str(e)}")
    
    async def payment(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Melakukan pembayaran melalui Digiflazz"""
        try:
            ref_id = request.get("transaction_code", self._generate_transaction_code())
            
            # Format data untuk Digiflazz
            payment_data = {
                "username": self.username,
                "buyer_sku_code": request["product_code"],
                "customer_no": request["customer_number"],
                "ref_id": ref_id,
                "sign": ""
            }
            
            # Buat signature
            payment_data["sign"] = self._create_signature(payment_data)
            
            logger.info(f"Digiflazz payment request: {payment_data}")
            
            # Panggil API Digiflazz
            response = await self._make_digiflazz_request("transaction", payment_data)
            
            # Parse response
            data = response.get("data", {})
            status = data.get("status", "").lower()
            
            if status == "sukses":
                result = {
                    "transaction_id": data.get("trx_id", ref_id),
                    "status": "success",
                    "message": data.get("message", "Pembayaran berhasil"),
                    "sn": data.get("sn", "")
                }
            elif status == "pending":
                result = {
                    "transaction_id": data.get("trx_id", ref_id),
                    "status": "pending",
                    "message": data.get("message", "Pembayaran sedang diproses")
                }
            else:
                result = {
                    "transaction_id": data.get("trx_id", ref_id),
                    "status": "failed",
                    "message": data.get("message", "Pembayaran gagal")
                }
            
            logger.info(f"Digiflazz payment result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Digiflazz payment error: {str(e)}")
            return {
                "transaction_id": request.get("transaction_code", ""),
                "status": "failed",
                "message": f"Pembayaran gagal: {str(e)}"
            }
    
    async def _make_digiflazz_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Helper method untuk membuat HTTP request ke Digiflazz"""
        url = f"{self.base_url}/{endpoint}"
        headers = self._get_headers()
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                async with session.post(url, json=data, headers=headers) as response:
                    response_text = await response.text()
                    logger.info(f"Digiflazz API response: {response.status} - {response_text}")
                    
                    if response.status == 200:
                        return await response.json()
                    else:
                        raise Exception(f"API Error: {response.status} - {response_text}")
                        
        except asyncio.TimeoutError:
            raise Exception("Request timeout")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")
    
    def get_supported_categories(self) -> List[PPOBCategory]:
        """Kategori yang didukung Digiflazz"""
        return [
            PPOBCategory.PULSA,
            PPOBCategory.LISTRIK,
            PPOBCategory.PDAM,
            PPOBCategory.INTERNET,
            PPOBCategory.BPJS,
            PPOBCategory.MULTIFINANCE
        ]
    
    async def get_balance(self) -> Dict[str, Any]:
        """Cek saldo Digiflazz"""
        try:
            ref_id = self._generate_transaction_code()
            
            balance_data = {
                "cmd": "deposit",
                "username": self.username,
                "sign": self._create_signature({"ref_id": ref_id})
            }
            
            response = await self._make_digiflazz_request("cek-saldo", balance_data)
            return response
            
        except Exception as e:
            logger.error(f"Digiflazz balance check error: {str(e)}")
            raise Exception(f"Gagal cek saldo: {str(e)}")
    
    async def get_price_list(self) -> Dict[str, Any]:
        """Ambil daftar harga produk dari Digiflazz"""
        try:
            ref_id = self._generate_transaction_code()
            
            price_data = {
                "cmd": "prepaid",
                "username": self.username,
                "sign": self._create_signature({"ref_id": ref_id})
            }
            
            response = await self._make_digiflazz_request("price-list", price_data)
            return response
            
        except Exception as e:
            logger.error(f"Digiflazz price list error: {str(e)}")
            raise Exception(f"Gagal ambil price list: {str(e)}")
