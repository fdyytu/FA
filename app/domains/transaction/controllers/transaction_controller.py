from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.core.database import get_db
from app.domains.transaction.services.transaction_service import TransactionService
from app.domains.transaction.schemas.transaction_schemas import TransactionCreate, TransactionUpdate
from app.domains.transaction.models.transaction import TransactionStatus, TransactionType
from app.common.responses.api_response import APIResponse

router = APIRouter()

def get_transaction_service(db: Session = Depends(get_db)) -> TransactionService:
    return TransactionService(db)

@router.post("/", response_model=dict)
async def create_transaction(
    transaction_data: TransactionCreate,
    service: TransactionService = Depends(get_transaction_service)
):
    """Create a new transaction"""
    return await service.create_transaction(transaction_data)

@router.get("/{transaction_id}", response_model=dict)
async def get_transaction(
    transaction_id: str = Path(..., description="Transaction ID"),
    service: TransactionService = Depends(get_transaction_service)
):
    """Get transaction by ID"""
    return await service.get_transaction(transaction_id)

@router.put("/{transaction_id}/status", response_model=dict)
async def update_transaction_status(
    transaction_id: str = Path(..., description="Transaction ID"),
    status: TransactionStatus = Query(..., description="New transaction status"),
    message: Optional[str] = Query(None, description="Status update message"),
    service: TransactionService = Depends(get_transaction_service)
):
    """Update transaction status"""
    return await service.update_transaction_status(transaction_id, status, message)

@router.get("/user/{user_id}", response_model=dict)
async def get_user_transactions(
    user_id: int = Path(..., description="User ID"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    service: TransactionService = Depends(get_transaction_service)
):
    """Get transactions for a specific user"""
    return await service.get_user_transactions(user_id, page, per_page)

@router.get("/status/{status}", response_model=dict)
async def get_transactions_by_status(
    status: TransactionStatus = Path(..., description="Transaction status"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    service: TransactionService = Depends(get_transaction_service)
):
    """Get transactions by status"""
    return await service.get_transactions_by_status(status, page, per_page)

@router.get("/type/{transaction_type}", response_model=dict)
async def get_transactions_by_type(
    transaction_type: TransactionType = Path(..., description="Transaction type"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    service: TransactionService = Depends(get_transaction_service)
):
    """Get transactions by type"""
    return await service.get_transactions_by_type(transaction_type, page, per_page)

@router.get("/", response_model=dict)
async def search_transactions(
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    status: Optional[TransactionStatus] = Query(None, description="Filter by status"),
    transaction_type: Optional[TransactionType] = Query(None, description="Filter by type"),
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    search_term: Optional[str] = Query(None, description="Search in transaction ID, description, or reference ID"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    service: TransactionService = Depends(get_transaction_service)
):
    """Search transactions with filters"""
    return await service.search_transactions(
        user_id=user_id,
        status=status,
        transaction_type=transaction_type,
        start_date=start_date,
        end_date=end_date,
        search_term=search_term,
        page=page,
        per_page=per_page
    )

@router.get("/stats/summary", response_model=dict)
async def get_transaction_stats(
    start_date: Optional[datetime] = Query(None, description="Start date for stats"),
    end_date: Optional[datetime] = Query(None, description="End date for stats"),
    service: TransactionService = Depends(get_transaction_service)
):
    """Get transaction statistics"""
    return await service.get_transaction_stats(start_date, end_date)

@router.get("/{transaction_id}/logs", response_model=dict)
async def get_transaction_logs(
    transaction_id: str = Path(..., description="Transaction ID"),
    service: TransactionService = Depends(get_transaction_service)
):
    """Get transaction logs"""
    return await service.get_transaction_logs(transaction_id)

@router.put("/{transaction_id}/cancel", response_model=dict)
async def cancel_transaction(
    transaction_id: str = Path(..., description="Transaction ID"),
    reason: Optional[str] = Query(None, description="Cancellation reason"),
    service: TransactionService = Depends(get_transaction_service)
):
    """Cancel a transaction"""
    return await service.cancel_transaction(transaction_id, reason)

# Create transaction controller instance
transaction_controller = type('TransactionController', (), {'router': router})()
