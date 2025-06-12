from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.product_service import ProductService, ProductStockService
from app.services.admin_auth_service import AdminAuthService
from app.schemas.product import (
    ProductCreate, ProductUpdate, ProductResponse,
    ProductStockResponse, AdminLoginRequest, AdminLoginResponse
)
from app.utils.responses import create_success_response
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()

def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency untuk mendapatkan admin yang sedang login"""
    token = credentials.credentials
    return AdminAuthService.get_current_admin(token)

# ===== ADMIN AUTHENTICATION =====

@router.post("/login", response_model=dict)
async def admin_login(login_data: AdminLoginRequest):
    """Login admin"""
    try:
        result = AdminAuthService.authenticate_admin(login_data)
        return create_success_response(
            message="Login berhasil",
            data=result.dict()
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error during admin login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Terjadi kesalahan saat login"
        )

# ===== PRODUCT MANAGEMENT =====

@router.post("/products", response_model=dict)
async def create_product(
    product_data: ProductCreate,
    admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Buat produk baru"""
    try:
        product_service = ProductService(db)
        product = product_service.create_product(product_data)
        
        logger.info(f"Admin {admin['username']} created product: {product.code}")
        
        return create_success_response(
            message="Produk berhasil dibuat",
            data=ProductResponse.from_orm(product).dict()
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error creating product: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal membuat produk: {str(e)}"
        )

@router.get("/products", response_model=dict)
async def get_all_products(
    skip: int = 0,
    limit: int = 100,
    admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Ambil semua produk"""
    try:
        product_service = ProductService(db)
        products = product_service.get_all_products(skip=skip, limit=limit)
        
        products_data = []
        stock_service = ProductStockService(db)
        
        for product in products:
            product_dict = ProductResponse.from_orm(product).dict()
            product_dict['total_stock'] = stock_service.get_total_stock(product.id)
            products_data.append(product_dict)
        
        return create_success_response(
            message="Data produk berhasil diambil",
            data=products_data
        )
    except Exception as e:
        logger.error(f"Error getting products: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal mengambil data produk: {str(e)}"
        )

@router.get("/products/{product_id}", response_model=dict)
async def get_product_detail(
    product_id: int,
    admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Ambil detail produk"""
    try:
        product_service = ProductService(db)
        product = product_service.get_product_by_id(product_id)
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produk tidak ditemukan"
            )
        
        stock_service = ProductStockService(db)
        product_dict = ProductResponse.from_orm(product).dict()
        product_dict['total_stock'] = stock_service.get_total_stock(product.id)
        product_dict['stock_history'] = [
            ProductStockResponse.from_orm(stock).dict() 
            for stock in stock_service.get_product_stocks(product.id)
        ]
        
        return create_success_response(
            message="Detail produk berhasil diambil",
            data=product_dict
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting product detail: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal mengambil detail produk: {str(e)}"
        )

@router.put("/products/{product_id}", response_model=dict)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update produk"""
    try:
        product_service = ProductService(db)
        product = product_service.update_product(product_id, product_data)
        
        logger.info(f"Admin {admin['username']} updated product: {product.code}")
        
        return create_success_response(
            message="Produk berhasil diupdate",
            data=ProductResponse.from_orm(product).dict()
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error updating product: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal update produk: {str(e)}"
        )

@router.delete("/products/{product_id}", response_model=dict)
async def delete_product(
    product_id: int,
    admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Hapus produk"""
    try:
        product_service = ProductService(db)
        product_service.delete_product(product_id)
        
        logger.info(f"Admin {admin['username']} deleted product ID: {product_id}")
        
        return create_success_response(
            message="Produk berhasil dihapus",
            data={"deleted_product_id": product_id}
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error deleting product: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal hapus produk: {str(e)}"
        )

# ===== STOCK MANAGEMENT =====

@router.post("/products/{product_id}/stock/upload", response_model=dict)
async def upload_stock_file(
    product_id: int,
    file: UploadFile = File(...),
    notes: str = Form(None),
    admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Upload file untuk menambah stock"""
    try:
        stock_service = ProductStockService(db)
        stock = stock_service.add_stock_from_file(product_id, file, notes)
        
        logger.info(f"Admin {admin['username']} uploaded stock file for product {product_id}: {stock.quantity} items")
        
        return create_success_response(
            message=f"Stock berhasil ditambahkan: {stock.quantity} item dari file {file.filename}",
            data=ProductStockResponse.from_orm(stock).dict()
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error uploading stock file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal upload file stock: {str(e)}"
        )

@router.get("/products/{product_id}/stock", response_model=dict)
async def get_product_stock(
    product_id: int,
    admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Ambil data stock produk"""
    try:
        stock_service = ProductStockService(db)
        stocks = stock_service.get_product_stocks(product_id)
        total_stock = stock_service.get_total_stock(product_id)
        
        stocks_data = [ProductStockResponse.from_orm(stock).dict() for stock in stocks]
        
        return create_success_response(
            message="Data stock berhasil diambil",
            data={
                "total_stock": total_stock,
                "stock_history": stocks_data
            }
        )
    except Exception as e:
        logger.error(f"Error getting product stock: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal mengambil data stock: {str(e)}"
        )

@router.delete("/stock/{stock_id}", response_model=dict)
async def delete_stock(
    stock_id: int,
    admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Hapus record stock"""
    try:
        stock_service = ProductStockService(db)
        stock_service.delete_stock(stock_id)
        
        logger.info(f"Admin {admin['username']} deleted stock ID: {stock_id}")
        
        return create_success_response(
            message="Record stock berhasil dihapus",
            data={"deleted_stock_id": stock_id}
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error deleting stock: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal hapus record stock: {str(e)}"
        )
