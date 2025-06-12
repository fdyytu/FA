from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.admin_service import AdminConfigService, PPOBMarginService
from app.schemas.admin import (
    AdminConfigCreate, AdminConfigUpdate, AdminConfigResponse,
    PPOBMarginConfigCreate, PPOBMarginConfigUpdate, PPOBMarginConfigResponse,
    DigiflazzConfigRequest, DigiflazzConfigResponse, MarginConfigRequest
)
from app.api.deps import get_current_active_user
from app.models.user import User
from app.utils.responses import create_success_response, create_paginated_response
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

def get_admin_user(current_user: Annotated[User, Depends(get_current_active_user)]):
    """Dependency untuk memastikan user adalah admin"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akses ditolak. Hanya admin yang dapat mengakses endpoint ini."
        )
    return current_user

# ===== KONFIGURASI DIGIFLAZZ =====

@router.post("/digiflazz/config", response_model=dict)
async def set_digiflazz_config(
    config_data: DigiflazzConfigRequest,
    admin_user: Annotated[User, Depends(get_admin_user)],
    db: Session = Depends(get_db)
):
    """Set konfigurasi Digiflazz"""
    try:
        admin_service = AdminConfigService(db)
        result = admin_service.set_digiflazz_config(config_data)
        
        logger.info(f"Admin {admin_user.username} updated Digiflazz config")
        
        return create_success_response(
            message="Konfigurasi Digiflazz berhasil disimpan",
            data=result
        )
    except Exception as e:
        logger.error(f"Error setting Digiflazz config: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal menyimpan konfigurasi: {str(e)}"
        )

@router.get("/digiflazz/config", response_model=dict)
async def get_digiflazz_config(
    admin_user: Annotated[User, Depends(get_admin_user)],
    db: Session = Depends(get_db)
):
    """Ambil konfigurasi Digiflazz"""
    try:
        admin_service = AdminConfigService(db)
        config = admin_service.get_digiflazz_config()
        
        # Jangan tampilkan API key untuk keamanan
        response_data = {
            "username": config["username"],
            "production": config["production"],
            "is_configured": config["is_configured"],
            "api_key_configured": bool(config["api_key"])
        }
        
        return create_success_response(
            message="Konfigurasi Digiflazz berhasil diambil",
            data=response_data
        )
    except Exception as e:
        logger.error(f"Error getting Digiflazz config: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal mengambil konfigurasi: {str(e)}"
        )

# ===== KONFIGURASI MARGIN =====

@router.post("/margin", response_model=dict)
async def create_margin_config(
    margin_data: MarginConfigRequest,
    admin_user: Annotated[User, Depends(get_admin_user)],
    db: Session = Depends(get_db)
):
    """Buat konfigurasi margin baru"""
    try:
        margin_service = PPOBMarginService(db)
        
        # Convert request ke create schema
        create_data = PPOBMarginConfigCreate(
            category=margin_data.category,
            product_code=margin_data.product_code,
            margin_type=margin_data.margin_type,
            margin_value=margin_data.margin_value,
            description=margin_data.description
        )
        
        margin_config = margin_service.create_margin_config(create_data)
        
        logger.info(f"Admin {admin_user.username} created margin config for {margin_data.category}")
        
        return create_success_response(
            message="Konfigurasi margin berhasil dibuat",
            data=PPOBMarginConfigResponse.from_orm(margin_config)
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error creating margin config: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal membuat konfigurasi margin: {str(e)}"
        )

@router.get("/margin", response_model=dict)
async def get_all_margin_configs(
    admin_user: Annotated[User, Depends(get_admin_user)],
    db: Session = Depends(get_db)
):
    """Ambil semua konfigurasi margin"""
    try:
        margin_service = PPOBMarginService(db)
        margin_configs = margin_service.get_all_margin_configs()
        
        configs_data = [
            PPOBMarginConfigResponse.from_orm(config) for config in margin_configs
        ]
        
        return create_success_response(
            message="Konfigurasi margin berhasil diambil",
            data=configs_data
        )
    except Exception as e:
        logger.error(f"Error getting margin configs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal mengambil konfigurasi margin: {str(e)}"
        )

@router.put("/margin/{margin_id}", response_model=dict)
async def update_margin_config(
    margin_id: int,
    update_data: PPOBMarginConfigUpdate,
    admin_user: Annotated[User, Depends(get_admin_user)],
    db: Session = Depends(get_db)
):
    """Update konfigurasi margin"""
    try:
        margin_service = PPOBMarginService(db)
        margin_config = margin_service.update_margin_config(margin_id, update_data)
        
        logger.info(f"Admin {admin_user.username} updated margin config ID: {margin_id}")
        
        return create_success_response(
            message="Konfigurasi margin berhasil diupdate",
            data=PPOBMarginConfigResponse.from_orm(margin_config)
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error updating margin config: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal update konfigurasi margin: {str(e)}"
        )

@router.delete("/margin/{margin_id}", response_model=dict)
async def delete_margin_config(
    margin_id: int,
    admin_user: Annotated[User, Depends(get_admin_user)],
    db: Session = Depends(get_db)
):
    """Hapus konfigurasi margin"""
    try:
        margin_service = PPOBMarginService(db)
        margin_service.delete_margin_config(margin_id)
        
        logger.info(f"Admin {admin_user.username} deleted margin config ID: {margin_id}")
        
        return create_success_response(
            message="Konfigurasi margin berhasil dihapus",
            data={"deleted_id": margin_id}
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error deleting margin config: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal hapus konfigurasi margin: {str(e)}"
        )

# ===== KONFIGURASI UMUM =====

@router.post("/config", response_model=dict)
async def create_admin_config(
    config_data: AdminConfigCreate,
    admin_user: Annotated[User, Depends(get_admin_user)],
    db: Session = Depends(get_db)
):
    """Buat konfigurasi admin baru"""
    try:
        admin_service = AdminConfigService(db)
        config = admin_service.create_config(config_data)
        
        logger.info(f"Admin {admin_user.username} created config: {config_data.config_key}")
        
        return create_success_response(
            message="Konfigurasi berhasil dibuat",
            data=AdminConfigResponse.from_orm(config)
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error creating admin config: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal membuat konfigurasi: {str(e)}"
        )

@router.get("/config", response_model=dict)
async def get_all_admin_configs(
    admin_user: Annotated[User, Depends(get_admin_user)],
    db: Session = Depends(get_db),
    include_encrypted: bool = Query(False, description="Sertakan konfigurasi terenkripsi")
):
    """Ambil semua konfigurasi admin"""
    try:
        admin_service = AdminConfigService(db)
        configs = admin_service.get_all_configs(include_encrypted=include_encrypted)
        
        configs_data = [
            AdminConfigResponse.from_orm(config) for config in configs
        ]
        
        return create_success_response(
            message="Konfigurasi admin berhasil diambil",
            data=configs_data
        )
    except Exception as e:
        logger.error(f"Error getting admin configs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal mengambil konfigurasi: {str(e)}"
        )

@router.get("/config/{config_key}", response_model=dict)
async def get_admin_config(
    config_key: str,
    admin_user: Annotated[User, Depends(get_admin_user)],
    db: Session = Depends(get_db)
):
    """Ambil konfigurasi admin berdasarkan key"""
    try:
        admin_service = AdminConfigService(db)
        config = admin_service.get_config(config_key, decrypt=False)  # Jangan decrypt untuk keamanan
        
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Konfigurasi tidak ditemukan"
            )
        
        return create_success_response(
            message="Konfigurasi berhasil diambil",
            data=AdminConfigResponse.from_orm(config)
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting admin config: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal mengambil konfigurasi: {str(e)}"
        )

@router.put("/config/{config_key}", response_model=dict)
async def update_admin_config(
    config_key: str,
    update_data: AdminConfigUpdate,
    admin_user: Annotated[User, Depends(get_admin_user)],
    db: Session = Depends(get_db)
):
    """Update konfigurasi admin"""
    try:
        admin_service = AdminConfigService(db)
        config = admin_service.update_config(config_key, update_data)
        
        logger.info(f"Admin {admin_user.username} updated config: {config_key}")
        
        return create_success_response(
            message="Konfigurasi berhasil diupdate",
            data=AdminConfigResponse.from_orm(config)
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error updating admin config: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal update konfigurasi: {str(e)}"
        )

@router.delete("/config/{config_key}", response_model=dict)
async def delete_admin_config(
    config_key: str,
    admin_user: Annotated[User, Depends(get_admin_user)],
    db: Session = Depends(get_db)
):
    """Hapus konfigurasi admin"""
    try:
        admin_service = AdminConfigService(db)
        admin_service.delete_config(config_key)
        
        logger.info(f"Admin {admin_user.username} deleted config: {config_key}")
        
        return create_success_response(
            message="Konfigurasi berhasil dihapus",
            data={"deleted_key": config_key}
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error deleting admin config: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal hapus konfigurasi: {str(e)}"
        )

# ===== TESTING DIGIFLAZZ =====

@router.post("/digiflazz/test-connection", response_model=dict)
async def test_digiflazz_connection(
    admin_user: Annotated[User, Depends(get_admin_user)],
    db: Session = Depends(get_db)
):
    """Test koneksi ke Digiflazz"""
    try:
        from app.services.ppob.providers.digiflazz_provider import DigiflazzProvider
        
        admin_service = AdminConfigService(db)
        config = admin_service.get_digiflazz_config()
        
        if not config["is_configured"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Konfigurasi Digiflazz belum lengkap"
            )
        
        # Test koneksi dengan cek saldo
        provider = DigiflazzProvider(
            username=config["username"],
            api_key=config["api_key"],
            production=config["production"]
        )
        
        balance_result = await provider.get_balance()
        
        logger.info(f"Admin {admin_user.username} tested Digiflazz connection")
        
        return create_success_response(
            message="Koneksi Digiflazz berhasil",
            data={
                "status": "connected",
                "balance_info": balance_result
            }
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error testing Digiflazz connection: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal test koneksi: {str(e)}"
        )

@router.get("/digiflazz/price-list", response_model=dict)
async def get_digiflazz_price_list(
    admin_user: Annotated[User, Depends(get_admin_user)],
    db: Session = Depends(get_db)
):
    """Ambil price list dari Digiflazz"""
    try:
        from app.services.ppob.providers.digiflazz_provider import DigiflazzProvider
        
        admin_service = AdminConfigService(db)
        config = admin_service.get_digiflazz_config()
        
        if not config["is_configured"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Konfigurasi Digiflazz belum lengkap"
            )
        
        provider = DigiflazzProvider(
            username=config["username"],
            api_key=config["api_key"],
            production=config["production"]
        )
        
        price_list = await provider.get_price_list()
        
        logger.info(f"Admin {admin_user.username} fetched Digiflazz price list")
        
        return create_success_response(
            message="Price list Digiflazz berhasil diambil",
            data=price_list
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting Digiflazz price list: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal ambil price list: {str(e)}"
        )
