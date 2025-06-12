"""
Transactions router - minimal implementation untuk testing
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_transactions():
    """Get transaction history"""
    return {"message": "Transaction history endpoint"}

@router.get("/{transaction_id}")
async def get_transaction(transaction_id: str):
    """Get specific transaction"""
    return {"message": f"Transaction {transaction_id} endpoint"}
