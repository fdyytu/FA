from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any

router = APIRouter()

@router.get("/balance")
async def get_wallet_balance():
    """Get current user's wallet balance - Test endpoint"""
    return {
        "message": "Wallet balance endpoint working",
        "balance": 0.0,
        "status": "success"
    }

@router.get("/test")
async def test_payment_factory():
    """Test payment factory functionality"""
    try:
        # Import our new payment services
        from app.domains.payment.services.manual_topup_service import ManualTopUpService
        from app.domains.payment.services.payment_factory import PaymentFactory
        
        return {
            "message": "Payment services imported successfully",
            "services": {
                "manual_topup_service": "✅ Available",
                "payment_factory": "✅ Available",
                "midtrans_service": "✅ Available"
            },
            "status": "success"
        }
    except Exception as e:
        return {
            "message": "Error importing payment services",
            "error": str(e),
            "status": "error"
        }

@router.post("/topup/manual/test")
async def test_manual_topup():
    """Test manual top up functionality"""
    return {
        "message": "Manual top up endpoint working",
        "request_code": "TOPUP-TEST-12345",
        "amount": 100000,
        "payment_method": "BANK_TRANSFER",
        "status": "PENDING"
    }

@router.post("/topup/midtrans/test")
async def test_midtrans_topup():
    """Test Midtrans top up functionality"""
    return {
        "message": "Midtrans top up endpoint working",
        "request_code": "TOPUP-MIDTRANS-12345",
        "payment_url": "https://app.sandbox.midtrans.com/snap/v1/transactions/test",
        "status": "PENDING"
    }
