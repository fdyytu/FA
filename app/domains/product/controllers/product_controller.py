from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal

from app.domains.product.services.product_service import ProductService, VoucherService
from app.domains.product.schemas.product_schemas import (
    ProductCreate, ProductUpdate, ProductResponse, ProductListResponse, ProductFilter,
    VoucherCreate, VoucherUpdate, VoucherResponse, VoucherFilter,
    VoucherValidationRequest, VoucherValidationResponse, VoucherUsageCreate
)
from app.infrastructure.database.database_manager import get_db
from app.shared.responses.api_response import create_response
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

def get_product_service(db: Session = Depends(get_db)) -> ProductService:
    """Dependency untuk mendapatkan ProductService"""
    return ProductService(db)

def get_voucher_service(db: Session = Depends(get_db)) -> VoucherService:
    """Dependency untuk mendapatkan VoucherService"""
    return VoucherService(db)

# ===== PRODUCT ENDPOINTS =====

@router.post("/products", response_model=dict, summary="Create Product")
async def create_product(
    product_data: ProductCreate,
    service: ProductService = Depends(get_product_service)
):
    """
    Membuat produk baru.
    
    - **name**: Nama produk
    - **slug**: URL slug produk (harus unik)
    - **category**: Kategori produk
    - **price**: Harga produk
    - **stock_quantity**: Jumlah stok
    """
    try:
        product = await service.create_product(product_data)
        
        return create_response(
            success=True,
            message="Produk berhasil dibuat",
            data={"product_id": product.id, "slug": product.slug}
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating product: {e}")
        raise HTTPException(status_code=500, detail="Gagal membuat produk")

@router.get("/products", response_model=dict, summary="Get Products")
async def get_products(
    category: Optional[str] = Query(None, description="Filter berdasarkan kategori"),
    subcategory: Optional[str] = Query(None, description="Filter berdasarkan sub-kategori"),
    min_price: Optional[Decimal] = Query(None, ge=0, description="Harga minimum"),
    max_price: Optional[Decimal] = Query(None, ge=0, description="Harga maksimum"),
    is_featured: Optional[bool] = Query(None, description="Filter produk unggulan"),
    status: Optional[str] = Query("active", description="Filter berdasarkan status"),
    search: Optional[str] = Query(None, description="Pencarian produk"),
    sort_by: Optional[str] = Query("created_at", description="Urutkan berdasarkan"),
    sort_order: Optional[str] = Query("desc", regex="^(asc|desc)$", description="Urutan sort"),
    limit: int = Query(20, ge=1, le=100, description="Jumlah maksimal data"),
    offset: int = Query(0, ge=0, description="Offset untuk pagination"),
    service: ProductService = Depends(get_product_service)
):
    """
    Mendapatkan daftar produk dengan filtering dan pagination.
    
    Mendukung filtering berdasarkan:
    - Kategori dan sub-kategori
    - Range harga
    - Status produk
    - Pencarian teks
    - Produk unggulan
    """
    try:
        filter_params = ProductFilter(
            category=category,
            subcategory=subcategory,
            min_price=min_price,
            max_price=max_price,
            is_featured=is_featured,
            status=status,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        products = await service.get_products(filter_params, limit, offset)
        
        # Convert to response format
        products_data = []
        for product in products:
            products_data.append({
                "id": product.id,
                "name": product.name,
                "slug": product.slug,
                "short_description": product.short_description,
                "category": product.category,
                "subcategory": product.subcategory,
                "price": float(product.price),
                "compare_at_price": float(product.compare_at_price) if product.compare_at_price else None,
                "featured_image": product.featured_image,
                "status": product.status,
                "is_featured": product.is_featured,
                "stock_quantity": product.stock_quantity,
                "rating_average": float(product.rating_average),
                "rating_count": product.rating_count,
                "view_count": product.view_count,
                "created_at": product.created_at.isoformat()
            })
        
        return create_response(
            success=True,
            message="Data produk berhasil diambil",
            data={
                "products": products_data,
                "total": len(products_data),
                "limit": limit,
                "offset": offset
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting products: {e}")
        raise HTTPException(status_code=500, detail="Gagal mengambil data produk")

@router.get("/products/{product_id}", response_model=dict, summary="Get Product by ID")
async def get_product_by_id(
    product_id: int,
    track_view: bool = Query(True, description="Track view untuk analytics"),
    service: ProductService = Depends(get_product_service)
):
    """
    Mendapatkan detail produk berdasarkan ID.
    
    - **product_id**: ID produk
    - **track_view**: Apakah view akan ditrack untuk analytics
    """
    try:
        product = await service.get_product_by_id(product_id, track_view)
        
        if not product:
            raise HTTPException(status_code=404, detail="Produk tidak ditemukan")
        
        # Parse JSON fields
        import json
        tags = json.loads(product.tags) if product.tags else []
        gallery_images = json.loads(product.gallery_images) if product.gallery_images else []
        
        product_data = {
            "id": product.id,
            "name": product.name,
            "slug": product.slug,
            "description": product.description,
            "short_description": product.short_description,
            "category": product.category,
            "subcategory": product.subcategory,
            "tags": tags,
            "price": float(product.price),
            "cost_price": float(product.cost_price) if product.cost_price else None,
            "compare_at_price": float(product.compare_at_price) if product.compare_at_price else None,
            "sku": product.sku,
            "stock_quantity": product.stock_quantity,
            "track_inventory": product.track_inventory,
            "allow_backorder": product.allow_backorder,
            "weight": float(product.weight) if product.weight else None,
            "dimensions": product.dimensions,
            "meta_title": product.meta_title,
            "meta_description": product.meta_description,
            "featured_image": product.featured_image,
            "gallery_images": gallery_images,
            "status": product.status,
            "is_featured": product.is_featured,
            "is_digital": product.is_digital,
            "requires_shipping": product.requires_shipping,
            "view_count": product.view_count,
            "purchase_count": product.purchase_count,
            "rating_average": float(product.rating_average),
            "rating_count": product.rating_count,
            "published_at": product.published_at.isoformat() if product.published_at else None,
            "created_at": product.created_at.isoformat(),
            "updated_at": product.updated_at.isoformat()
        }
        
        return create_response(
            success=True,
            message="Detail produk berhasil diambil",
            data=product_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting product by ID: {e}")
        raise HTTPException(status_code=500, detail="Gagal mengambil detail produk")

@router.get("/products/featured", response_model=dict, summary="Get Featured Products")
async def get_featured_products(
    limit: int = Query(10, ge=1, le=50, description="Jumlah produk unggulan"),
    service: ProductService = Depends(get_product_service)
):
    """
    Mendapatkan daftar produk unggulan.
    
    - **limit**: Jumlah maksimal produk yang dikembalikan
    """
    try:
        products = await service.get_featured_products(limit)
        
        products_data = []
        for product in products:
            products_data.append({
                "id": product.id,
                "name": product.name,
                "slug": product.slug,
                "short_description": product.short_description,
                "category": product.category,
                "price": float(product.price),
                "compare_at_price": float(product.compare_at_price) if product.compare_at_price else None,
                "featured_image": product.featured_image,
                "rating_average": float(product.rating_average),
                "rating_count": product.rating_count
            })
        
        return create_response(
            success=True,
            message="Produk unggulan berhasil diambil",
            data={"products": products_data}
        )
        
    except Exception as e:
        logger.error(f"Error getting featured products: {e}")
        raise HTTPException(status_code=500, detail="Gagal mengambil produk unggulan")

@router.post("/vouchers", response_model=dict, summary="Create Voucher")
async def create_voucher(
    voucher_data: VoucherCreate,
    service: VoucherService = Depends(get_voucher_service)
):
    """
    Membuat voucher baru.
    
    - **code**: Kode voucher (harus unik)
    - **name**: Nama voucher
    - **voucher_type**: Tipe voucher (percentage, fixed_amount, etc.)
    - **discount_value**: Nilai diskon
    - **valid_from**: Tanggal mulai berlaku
    - **valid_until**: Tanggal berakhir
    """
    try:
        voucher = await service.create_voucher(voucher_data)
        
        return create_response(
            success=True,
            message="Voucher berhasil dibuat",
            data={"voucher_id": voucher.id, "code": voucher.code}
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating voucher: {e}")
        raise HTTPException(status_code=500, detail="Gagal membuat voucher")

@router.post("/vouchers/validate", response_model=dict, summary="Validate Voucher")
async def validate_voucher(
    validation_request: VoucherValidationRequest,
    service: VoucherService = Depends(get_voucher_service)
):
    """
    Validasi voucher sebelum digunakan.
    
    - **code**: Kode voucher
    - **user_id**: ID user
    - **order_amount**: Total order
    - **product_ids**: ID produk dalam order (optional)
    """
    try:
        validation_result = await service.validate_voucher(validation_request)
        
        return create_response(
            success=True,
            message="Validasi voucher selesai",
            data={
                "is_valid": validation_result.is_valid,
                "discount_amount": float(validation_result.discount_amount),
                "message": validation_result.message,
                "voucher_id": validation_result.voucher_id,
                "voucher_name": validation_result.voucher_name
            }
        )
        
    except Exception as e:
        logger.error(f"Error validating voucher: {e}")
        raise HTTPException(status_code=500, detail="Gagal melakukan validasi voucher")
