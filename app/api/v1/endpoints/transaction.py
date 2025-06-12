from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.services.transaction_service import TransactionService, DailyMutationService
from app.schemas.transaction import (
    TransactionCreate, TransactionUpdate, TransactionResponse,
    TransactionHistoryResponse, DailyMutationResponse, TransactionSummaryResponse,
    TransactionFilterRequest, TransactionTypeEnum, TransactionStatusEnum
)
from app.utils.responses import create_success_response, create_error_response
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/", response_model=dict)
async def create_transaction(
    transaction_data: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Membuat transaksi baru"""
    try:
        # Set user_id dari current_user jika tidak ada
        if not transaction_data.user_id:
            transaction_data.user_id = current_user.id
        
        # Cek apakah user bisa membuat transaksi untuk user lain (admin only)
        if transaction_data.user_id != current_user.id and not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="Tidak dapat membuat transaksi untuk user lain")
        
        service = TransactionService(db)
        transaction = await service.create_transaction(transaction_data)
        
        return create_success_response(
            data=transaction.dict(),
            message="Transaksi berhasil dibuat"
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error creating transaction: {str(e)}")
        return create_error_response(message=f"Gagal membuat transaksi: {str(e)}")

@router.put("/{transaction_id}", response_model=dict)
async def update_transaction(
    transaction_id: int,
    update_data: TransactionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update status transaksi (untuk admin atau sistem)"""
    try:
        # Hanya admin yang bisa update transaksi
        if not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="Akses ditolak")
        
        service = TransactionService(db)
        transaction = await service.update_transaction(transaction_id, update_data)
        
        return create_success_response(
            data=transaction.dict(),
            message="Transaksi berhasil diupdate"
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error updating transaction: {str(e)}")
        return create_error_response(message=f"Gagal update transaksi: {str(e)}")

@router.get("/history", response_model=dict)
async def get_transaction_history(
    user_id: Optional[int] = Query(None),
    transaction_type: Optional[TransactionTypeEnum] = Query(None),
    status: Optional[TransactionStatusEnum] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mendapatkan riwayat transaksi dengan filter"""
    try:
        # Jika bukan admin, hanya bisa melihat transaksi sendiri
        if not current_user.is_superuser:
            user_id = current_user.id
        
        filter_request = TransactionFilterRequest(
            user_id=user_id,
            transaction_type=transaction_type,
            status=status,
            start_date=start_date,
            end_date=end_date,
            page=page,
            limit=limit
        )
        
        service = TransactionService(db)
        transactions = await service.get_transaction_history(filter_request)
        
        return create_success_response(
            data={
                "transactions": [t.dict() for t in transactions],
                "page": page,
                "limit": limit,
                "filters": filter_request.dict(exclude_unset=True)
            },
            message="Riwayat transaksi berhasil diambil"
        )
        
    except Exception as e:
        logger.error(f"Error getting transaction history: {str(e)}")
        return create_error_response(message=f"Gagal mengambil riwayat transaksi: {str(e)}")

@router.get("/summary", response_model=dict)
async def get_transaction_summary(
    user_id: Optional[int] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mendapatkan ringkasan transaksi"""
    try:
        # Jika bukan admin, hanya bisa melihat ringkasan sendiri
        if not current_user.is_superuser:
            user_id = current_user.id
        
        service = TransactionService(db)
        summary = await service.get_transaction_summary(user_id, start_date, end_date)
        
        return create_success_response(
            data=summary.dict(),
            message="Ringkasan transaksi berhasil diambil"
        )
        
    except Exception as e:
        logger.error(f"Error getting transaction summary: {str(e)}")
        return create_error_response(message=f"Gagal mengambil ringkasan transaksi: {str(e)}")

# Endpoints untuk mutasi harian (admin only)
@router.post("/daily-mutation/generate", response_model=dict)
async def generate_daily_mutation(
    target_date: date = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate mutasi harian untuk tanggal tertentu (admin only)"""
    try:
        if not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="Akses ditolak")
        
        service = DailyMutationService(db)
        mutation = await service.generate_daily_mutation(target_date)
        
        return create_success_response(
            data=mutation.dict(),
            message=f"Mutasi harian berhasil dibuat untuk {target_date}"
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error generating daily mutation: {str(e)}")
        return create_error_response(message=f"Gagal generate mutasi harian: {str(e)}")

@router.get("/daily-mutation", response_model=dict)
async def get_daily_mutations(
    start_date: date = Query(...),
    end_date: date = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mendapatkan mutasi harian dalam rentang tanggal (admin only)"""
    try:
        if not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="Akses ditolak")
        
        service = DailyMutationService(db)
        mutations = await service.get_daily_mutations(start_date, end_date)
        
        return create_success_response(
            data={
                "mutations": [m.dict() for m in mutations],
                "start_date": start_date,
                "end_date": end_date,
                "total_days": len(mutations)
            },
            message="Mutasi harian berhasil diambil"
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting daily mutations: {str(e)}")
        return create_error_response(message=f"Gagal mengambil mutasi harian: {str(e)}")

@router.get("/daily-mutation/summary", response_model=dict)
async def get_mutation_summary(
    start_date: date = Query(...),
    end_date: date = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mendapatkan ringkasan mutasi dalam periode tertentu (admin only)"""
    try:
        if not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="Akses ditolak")
        
        service = DailyMutationService(db)
        summary = await service.get_mutation_summary(start_date, end_date)
        
        return create_success_response(
            data=summary,
            message="Ringkasan mutasi berhasil diambil"
        )
        
    except Exception as e:
        logger.error(f"Error getting mutation summary: {str(e)}")
        return create_error_response(message=f"Gagal mengambil ringkasan mutasi: {str(e)}")

@router.post("/daily-mutation/auto-generate", response_model=dict)
async def auto_generate_daily_mutation(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Auto generate mutasi harian untuk kemarin (admin only)"""
    try:
        if not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="Akses ditolak")
        
        service = DailyMutationService(db)
        await service.auto_generate_daily_mutations()
        
        return create_success_response(
            data=None,
            message="Auto generate mutasi harian berhasil"
        )
        
    except Exception as e:
        logger.error(f"Error auto generating daily mutation: {str(e)}")
        return create_error_response(message=f"Gagal auto generate mutasi harian: {str(e)}")
