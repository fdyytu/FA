"""
Registry untuk semua model database
File ini memastikan semua model diimport sehingga SQLAlchemy dapat membuat tabel
"""
import logging

logger = logging.getLogger(__name__)

def import_all_models():
    """
    Import semua model untuk memastikan mereka terdaftar di SQLAlchemy Base
    """
    models_imported = []
    
    try:
        # Admin models - WAJIB untuk sistem admin
        from app.domains.admin.models.admin import (
            Admin, AdminConfig, PPOBMarginConfig, 
            AdminAuditLog, AdminNotificationSetting
        )
        models_imported.extend([
            "Admin", "AdminConfig", "PPOBMarginConfig", 
            "AdminAuditLog", "AdminNotificationSetting"
        ])
        logger.info("Admin models imported successfully")
    except ImportError as e:
        logger.error(f"Failed to import admin models: {e}")
        
    try:
        # Auth/User models
        from app.domains.auth.models.user import User
        models_imported.append("User")
        logger.info("User models imported successfully")
    except ImportError as e:
        logger.warning(f"User models not available: {e}")
        
    try:
        # Discord models
        from app.domains.discord.models.discord_config import DiscordConfig
        models_imported.append("DiscordConfig")
        logger.info("Discord models imported successfully")
    except ImportError as e:
        logger.warning(f"Discord models not available: {e}")
        
    try:
        # Wallet models
        from app.domains.wallet.models.wallet import WalletTransaction, Transfer, TopUpRequest
        models_imported.extend(["WalletTransaction", "Transfer", "TopUpRequest"])
        logger.info("Wallet models imported successfully")
    except ImportError as e:
        logger.warning(f"Wallet models not available: {e}")
        
    try:
        # Product models
        from app.domains.product.models.product import Product
        models_imported.append("Product")
        logger.info("Product models imported successfully")
    except ImportError as e:
        logger.warning(f"Product models not available: {e}")
        
    try:
        # Voucher models
        from app.domains.voucher.models.voucher import Voucher, VoucherUsage
        models_imported.extend(["Voucher", "VoucherUsage"])
        logger.info("Voucher models imported successfully")
    except ImportError as e:
        logger.warning(f"Voucher models not available: {e}")
        
    try:
        # Analytics models
        from app.domains.analytics.models.analytic import (
            UserAnalytics, ProductAnalytics, VoucherAnalytics, DashboardMetrics
        )
        models_imported.extend([
            "UserAnalytics", "ProductAnalytics", "VoucherAnalytics", "DashboardMetrics"
        ])
        logger.info("Analytics models imported successfully")
    except ImportError as e:
        logger.warning(f"Analytics models not available: {e}")
        
    try:
        # PPOB models
        from app.domains.ppob.models.ppob import PPOBTransaction, PPOBProduct
        models_imported.extend(["PPOBTransaction", "PPOBProduct"])
        logger.info("PPOB models imported successfully")
    except ImportError as e:
        logger.warning(f"PPOB models not available: {e}")
        
    try:
        # Transaction models
        from app.domains.transaction.models.transaction import Transaction, TransactionLog
        models_imported.extend(["Transaction", "TransactionLog"])
        logger.info("Transaction models imported successfully")
    except ImportError as e:
        logger.warning(f"Transaction models not available: {e}")
    
    logger.info(f"Total models imported: {len(models_imported)} - {models_imported}")
    return models_imported
