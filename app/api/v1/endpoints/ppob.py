from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.ppob_service import PPOBService
from app.schemas.ppob import (
    PPOBInquiryRequest, PPOBInquiryResponse, PPOBPaymentRequest,
    PPOBTransactionResponse, PPOBProductResponse, PPOBCategoryResponse
)
from app.models.ppob import PPOBCategory
from app.api.deps import get_current_active_user
from app.models.user import User
from app.utils.responses import create_success_response, create_paginated_response

router = APIRouter()

@router.get("/categories", response_model=dict)
async def get_categories():
    """Ambil daftar kategori PPOB"""
    categories = [
        {"value": category.value, "name": category.value.title()}
        for category in PPOBCategory
    ]
    
    return create_success_response(
        message="Kategori PPOB berhasil diambil",
        data=categories
    )

@router.get("/products/{category}", response_model=dict)
async def get_products_by_category(
    category: PPOBCategory,
    db: Session = Depends(get_db)
):
    """Ambil produk berdasarkan kategori"""
    try:
        ppob_service = PPOBService(db)
        products = ppob_service.get_products_by_category(category)
        
        products_data = [
            PPOBProductResponse.from_orm(product) for product in products
        ]
        
        return create_success_response(
            message=f"Produk {category.value} berhasil diambil",
            data=products_data
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal mengambil produk: {str(e)}"
        )

@router.post("/inquiry", response_model=dict)
async def inquiry_bill(
    request: PPOBInquiryRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db)
):
    """Inquiry tagihan PPOB"""
    try:
        ppob_service = PPOBService(db)
        inquiry_result = await ppob_service.inquiry(request)
        
        return create_success_response(
            message="Inquiry berhasil",
            data=inquiry_result
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal melakukan inquiry: {str(e)}"
        )

@router.post("/payment", response_model=dict)
async def create_payment(
    request: PPOBPaymentRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db)
):
    """Buat transaksi pembayaran PPOB"""
    try:
        ppob_service = PPOBService(db)
        transaction = await ppob_service.create_transaction(current_user, request)
        
        return create_success_response(
            message="Transaksi berhasil dibuat",
            data=PPOBTransactionResponse.from_orm(transaction)
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal membuat transaksi: {str(e)}"
        )

@router.post("/payment/{transaction_id}/process", response_model=dict)
async def process_payment(
    transaction_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db)
):
    """Proses pembayaran transaksi"""
    try:
        ppob_service = PPOBService(db)
        
        # Verifikasi transaksi milik user
        transaction = ppob_service.get_transaction_by_id(transaction_id)
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaksi tidak ditemukan"
            )
        
        if transaction.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tidak memiliki akses ke transaksi ini"
            )
        
        processed_transaction = await ppob_service.process_payment(transaction_id)
        
        return create_success_response(
            message="Pembayaran berhasil diproses",
            data=PPOBTransactionResponse.from_orm(processed_transaction)
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal memproses pembayaran: {str(e)}"
        )

@router.get("/transactions", response_model=dict)
async def get_transaction_history(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Halaman"),
    size: int = Query(10, ge=1, le=100, description="Jumlah data per halaman")
):
    """Ambil riwayat transaksi user"""
    try:
        ppob_service = PPOBService(db)
        skip = (page - 1) * size
        
        transactions = ppob_service.get_user_transactions(
            current_user.id, skip=skip, limit=size
        )
        
        # Hitung total transaksi untuk pagination
        from app.models.ppob import PPOBTransaction
        total = db.query(PPOBTransaction).filter(
            PPOBTransaction.user_id == current_user.id
        ).count()
        
        transactions_data = [
            PPOBTransactionResponse.from_orm(transaction) 
            for transaction in transactions
        ]
        
        return create_paginated_response(
            data=transactions_data,
            total=total,
            page=page,
            size=size,
            message="Riwayat transaksi berhasil diambil"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal mengambil riwayat transaksi: {str(e)}"
        )

@router.get("/transactions/{transaction_id}", response_model=dict)
async def get_transaction_detail(
    transaction_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db)
):
    """Ambil detail transaksi"""
    try:
        ppob_service = PPOBService(db)
        transaction = ppob_service.get_transaction_by_id(transaction_id)
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaksi tidak ditemukan"
            )
        
        if transaction.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tidak memiliki akses ke transaksi ini"
            )
        
        return create_success_response(
            message="Detail transaksi berhasil diambil",
            data=PPOBTransactionResponse.from_orm(transaction)
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal mengambil detail transaksi: {str(e)}"
        )
