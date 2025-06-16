from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.domains.admin.services.admin_service import (
    AdminAuthService, AdminManagementService, ConfigurationService,
    MarginManagementService, UserManagementService, ProductManagementService,
    DashboardService
)
from app.domains.admin.schemas.admin_schemas import (
    AdminLogin, AdminLoginResponse, AdminCreate, AdminUpdate, AdminResponse,
    ConfigCreate, ConfigUpdate, ConfigResponse, MarginConfigCreate, 
    MarginConfigUpdate, MarginConfigResponse, UserManagementResponse,
    UserUpdateByAdmin, ProductCreate, ProductUpdate, ProductResponse,
    DashboardResponse, PaginationParams, PaginatedResponse, AuditLogResponse,
    DiscordConfigCreate, DiscordConfigUpdate, DiscordConfigResponse
)
from app.domains.discord.schemas.discord_admin_schemas import (
    DiscordLogResponse, DiscordCommandResponse, DiscordStatsResponse,
    PaginatedDiscordLogsResponse, PaginatedDiscordCommandsResponse
)
from app.shared.dependencies.admin_auth_deps import get_current_admin, get_current_super_admin
from app.domains.admin.models.admin import Admin
from app.common.security.auth_security import create_access_token
from app.shared.responses.api_response import APIResponse


class AdminAuthController:
    """
    Controller untuk autentikasi admin - Single Responsibility: Admin authentication endpoints
    """
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup routes untuk autentikasi admin"""
        
        @self.router.post("/login", response_model=AdminLoginResponse)
        async def login_admin(
            login_data: AdminLogin,
            request: Request,
            db: Session = Depends(get_db)
        ):
            """Login admin"""
            auth_service = AdminAuthService(db)
            
            admin = auth_service.authenticate_admin(
                login_data.username, 
                login_data.password
            )
            
            if not admin:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Username atau password salah"
                )
            
            # Create access token
            access_token = create_access_token(
                data={"sub": str(admin.id), "type": "admin"}
            )
            
            return AdminLoginResponse(
                access_token=access_token,
                admin=AdminResponse.from_orm(admin)
            )
        
        @self.router.post("/logout")
        async def logout_admin(
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Logout admin"""
            # Log logout activity
            from app.domains.admin.repositories.admin_repository import AuditLogRepository
            audit_repo = AuditLogRepository(db)
            audit_repo.create_log(
                admin_id=current_admin.id,
                action="LOGOUT",
                resource="admin",
                resource_id=current_admin.id
            )
            
            return APIResponse.success(message="Logout berhasil")


class AdminManagementController:
    """
    Controller untuk manajemen admin - Single Responsibility: Admin management endpoints
    """
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup routes untuk manajemen admin"""
        
        @self.router.get("/", response_model=PaginatedResponse)
        async def get_admins(
            page: int = 1,
            size: int = 10,
            current_admin: Admin = Depends(get_current_super_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil daftar admin"""
            admin_service = AdminManagementService(db)
            skip = (page - 1) * size
            
            admins, total = admin_service.get_admins(skip, size)
            
            return PaginatedResponse(
                items=[AdminResponse.from_orm(admin) for admin in admins],
                total=total,
                page=page,
                size=size,
                pages=(total + size - 1) // size
            )
        
        @self.router.post("/", response_model=AdminResponse)
        async def create_admin(
            admin_data: AdminCreate,
            current_admin: Admin = Depends(get_current_super_admin),
            db: Session = Depends(get_db)
        ):
            """Buat admin baru"""
            auth_service = AdminAuthService(db)
            
            admin = auth_service.create_admin(admin_data, current_admin.id)
            
            return AdminResponse.from_orm(admin)
        
        @self.router.get("/{admin_id}", response_model=AdminResponse)
        async def get_admin(
            admin_id: str,
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil admin berdasarkan ID"""
            admin_service = AdminManagementService(db)
            
            admin = admin_service.get_admin_by_id(admin_id)
            
            return AdminResponse.from_orm(admin)
        
        @self.router.put("/{admin_id}", response_model=AdminResponse)
        async def update_admin(
            admin_id: str,
            admin_data: AdminUpdate,
            current_admin: Admin = Depends(get_current_super_admin),
            db: Session = Depends(get_db)
        ):
            """Update admin"""
            admin_service = AdminManagementService(db)
            
            admin = admin_service.update_admin(admin_id, admin_data, current_admin.id)
            
            return AdminResponse.from_orm(admin)
        
        @self.router.delete("/{admin_id}")
        async def delete_admin(
            admin_id: str,
            current_admin: Admin = Depends(get_current_super_admin),
            db: Session = Depends(get_db)
        ):
            """Hapus admin"""
            admin_service = AdminManagementService(db)
            
            success = admin_service.delete_admin(admin_id, current_admin.id)
            
            if success:
                return APIResponse.success(message="Admin berhasil dihapus")
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Gagal menghapus admin"
                )


class ConfigurationController:
    """
    Controller untuk manajemen konfigurasi - Single Responsibility: Configuration management endpoints
    """
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup routes untuk manajemen konfigurasi"""
        
        @self.router.get("/", response_model=PaginatedResponse)
        async def get_configs(
            page: int = 1,
            size: int = 10,
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil daftar konfigurasi"""
            config_service = ConfigurationService(db)
            skip = (page - 1) * size
            
            configs, total = config_service.get_all_configs(skip, size)
            
            return PaginatedResponse(
                items=[ConfigResponse.from_orm(config) for config in configs],
                total=total,
                page=page,
                size=size,
                pages=(total + size - 1) // size
            )
        
        @self.router.post("/", response_model=ConfigResponse)
        async def create_config(
            config_data: ConfigCreate,
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Buat konfigurasi baru"""
            config_service = ConfigurationService(db)
            
            config = config_service.create_config(config_data, current_admin.id)
            
            return ConfigResponse.from_orm(config)
        
        @self.router.get("/{config_key}")
        async def get_config(
            config_key: str,
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil konfigurasi berdasarkan key"""
            config_service = ConfigurationService(db)
            
            config = config_service.get_config(config_key)
            
            if not config:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Konfigurasi tidak ditemukan"
                )
            
            return ConfigResponse.from_orm(config)
        
        @self.router.put("/{config_id}", response_model=ConfigResponse)
        async def update_config(
            config_id: str,
            config_data: ConfigUpdate,
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Update konfigurasi"""
            config_service = ConfigurationService(db)
            
            config = config_service.update_config(config_id, config_data, current_admin.id)
            
            return ConfigResponse.from_orm(config)


class UserManagementController:
    """
    Controller untuk manajemen user - Single Responsibility: User management endpoints
    """
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup routes untuk manajemen user"""
        
        @self.router.get("/", response_model=PaginatedResponse)
        async def get_users(
            page: int = 1,
            size: int = 10,
            search: Optional[str] = None,
            is_active: Optional[bool] = None,
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil daftar user"""
            user_service = UserManagementService(db)
            skip = (page - 1) * size
            
            users, total = user_service.get_users(skip, size, search, is_active)
            
            return PaginatedResponse(
                items=[UserManagementResponse.from_orm(user) for user in users],
                total=total,
                page=page,
                size=size,
                pages=(total + size - 1) // size
            )
        
        @self.router.get("/stats")
        async def get_user_stats(
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil statistik user"""
            user_service = UserManagementService(db)
            
            stats = user_service.get_user_stats()
            
            return APIResponse.success(data=stats)
        
        @self.router.put("/{user_id}", response_model=UserManagementResponse)
        async def update_user(
            user_id: str,
            user_data: UserUpdateByAdmin,
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Update user"""
            user_service = UserManagementService(db)
            
            user = user_service.update_user(user_id, user_data, current_admin.id)
            
            return UserManagementResponse.from_orm(user)


class ProductManagementController:
    """
    Controller untuk manajemen produk - Single Responsibility: Product management endpoints
    """
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup routes untuk manajemen produk"""
        
        @self.router.get("/", response_model=PaginatedResponse)
        async def get_products(
            page: int = 1,
            size: int = 10,
            search: Optional[str] = None,
            category: Optional[str] = None,
            is_active: Optional[bool] = None,
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil daftar produk"""
            product_service = ProductManagementService(db)
            skip = (page - 1) * size
            
            products, total = product_service.get_products(
                skip, size, search, category, is_active
            )
            
            return PaginatedResponse(
                items=[ProductResponse.from_orm(product) for product in products],
                total=total,
                page=page,
                size=size,
                pages=(total + size - 1) // size
            )
        
        @self.router.get("/categories")
        async def get_product_categories(
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil semua kategori produk"""
            product_service = ProductManagementService(db)
            
            categories = product_service.get_product_categories()
            
            return APIResponse.success(data=categories)
        
        @self.router.post("/", response_model=ProductResponse)
        async def create_product(
            product_data: ProductCreate,
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Buat produk baru"""
            product_service = ProductManagementService(db)
            
            product = product_service.create_product(product_data, current_admin.id)
            
            return ProductResponse.from_orm(product)
        
        @self.router.put("/{product_id}", response_model=ProductResponse)
        async def update_product(
            product_id: str,
            product_data: ProductUpdate,
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Update produk"""
            product_service = ProductManagementService(db)
            
            product = product_service.update_product(
                product_id, product_data, current_admin.id
            )
            
            return ProductResponse.from_orm(product)


class DashboardController:
    """
    Controller untuk dashboard - Single Responsibility: Dashboard endpoints
    """
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup routes untuk dashboard"""
        
        @self.router.get("/", response_model=DashboardResponse)
        async def get_dashboard(
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil data dashboard"""
            dashboard_service = DashboardService(db)
            
            dashboard_data = dashboard_service.get_dashboard_data()
            
            return dashboard_data
        
        @self.router.get("/stats")
        async def get_dashboard_stats(
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil statistik dashboard"""
            dashboard_service = DashboardService(db)
            
            stats = dashboard_service.get_dashboard_stats()
            
            return APIResponse.success(data=stats)


class MarginManagementController:
    """
    Controller untuk manajemen margin - Single Responsibility: Margin management endpoints
    """
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup routes untuk manajemen margin"""
        
        @self.router.get("/", response_model=PaginatedResponse)
        async def get_margin_configs(
            page: int = 1,
            size: int = 10,
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil daftar konfigurasi margin"""
            from app.domains.admin.repositories.admin_repository import PPOBMarginRepository
            margin_repo = PPOBMarginRepository(db)
            skip = (page - 1) * size
            
            configs, total = margin_repo.get_all_with_pagination(skip, size)
            
            return PaginatedResponse(
                items=[MarginConfigResponse.from_orm(config) for config in configs],
                total=total,
                page=page,
                size=size,
                pages=(total + size - 1) // size
            )
        
        @self.router.post("/", response_model=MarginConfigResponse)
        async def create_margin_config(
            margin_data: MarginConfigCreate,
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Buat konfigurasi margin baru"""
            margin_service = MarginManagementService(db)
            
            config = margin_service.create_margin_config(margin_data, current_admin.id)
            
            return MarginConfigResponse.from_orm(config)
        
        @self.router.put("/{config_id}", response_model=MarginConfigResponse)
        async def update_margin_config(
            config_id: str,
            margin_data: MarginConfigUpdate,
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Update konfigurasi margin"""
            margin_service = MarginManagementService(db)
            
            config = margin_service.update_margin_config(
                config_id, margin_data, current_admin.id
            )
            
            return MarginConfigResponse.from_orm(config)


class DiscordConfigController:
    """
    Controller untuk manajemen konfigurasi Discord - Single Responsibility: Discord config management endpoints
    """
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup routes untuk manajemen konfigurasi Discord"""
        
        @self.router.get("/", response_model=PaginatedResponse)
        async def get_discord_configs(
            page: int = 1,
            size: int = 10,
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil daftar konfigurasi Discord"""
            from app.domains.discord.services.discord_config_service import discord_config_service
            
            skip = (page - 1) * size
            configs = discord_config_service.get_all_configs(db, skip=skip, limit=size)
            
            # Get total count
            total_configs = discord_config_service.get_all_configs(db, skip=0, limit=1000)
            total = len(total_configs)
            
            return PaginatedResponse(
                items=[DiscordConfigResponse.from_orm(config) for config in configs],
                total=total,
                page=page,
                size=size,
                pages=(total + size - 1) // size
            )
        
        @self.router.post("/", response_model=DiscordConfigResponse)
        async def create_discord_config(
            config_data: DiscordConfigCreate,
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Buat konfigurasi Discord baru"""
            from app.domains.discord.services.discord_config_service import discord_config_service
            from app.domains.discord.schemas.discord_config_schemas import DiscordConfigCreate as OriginalDiscordConfigCreate
            
            # Convert admin schema to discord schema
            original_config_data = OriginalDiscordConfigCreate(
                name=config_data.name,
                token=config_data.token,
                guild_id=config_data.guild_id,
                command_prefix=config_data.command_prefix,
                is_active=config_data.is_active
            )
            
            config = discord_config_service.create_config(db, original_config_data)
            
            # Log audit
            from app.domains.admin.repositories.admin_repository import AuditLogRepository
            audit_repo = AuditLogRepository(db)
            audit_repo.create_log(
                admin_id=current_admin.id,
                action="CREATE",
                resource="discord_config",
                resource_id=str(config.id)
            )
            
            return DiscordConfigResponse.from_orm(config)
        
        @self.router.get("/active", response_model=Optional[DiscordConfigResponse])
        async def get_active_discord_config(
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil konfigurasi Discord yang aktif"""
            from app.domains.discord.services.discord_config_service import discord_config_service
            
            config = discord_config_service.get_active_config(db)
            
            if not config:
                return None
            
            return DiscordConfigResponse.from_orm(config)
        
        @self.router.get("/{config_id}", response_model=DiscordConfigResponse)
        async def get_discord_config(
            config_id: int,
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil konfigurasi Discord berdasarkan ID"""
            from app.domains.discord.services.discord_config_service import discord_config_service
            
            config = discord_config_service.get_config(db, config_id)
            
            if not config:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Konfigurasi Discord tidak ditemukan"
                )
            
            return DiscordConfigResponse.from_orm(config)
        
        @self.router.put("/{config_id}", response_model=DiscordConfigResponse)
        async def update_discord_config(
            config_id: int,
            config_data: DiscordConfigUpdate,
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Update konfigurasi Discord"""
            from app.domains.discord.services.discord_config_service import discord_config_service
            from app.domains.discord.schemas.discord_config_schemas import DiscordConfigUpdate as OriginalDiscordConfigUpdate
            
            # Convert admin schema to discord schema
            original_config_data = OriginalDiscordConfigUpdate(
                name=config_data.name,
                token=config_data.token,
                guild_id=config_data.guild_id,
                command_prefix=config_data.command_prefix,
                is_active=config_data.is_active
            )
            
            config = discord_config_service.update_config(db, config_id, original_config_data)
            
            if not config:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Konfigurasi Discord tidak ditemukan"
                )
            
            # Log audit
            from app.domains.admin.repositories.admin_repository import AuditLogRepository
            audit_repo = AuditLogRepository(db)
            audit_repo.create_log(
                admin_id=current_admin.id,
                action="UPDATE",
                resource="discord_config",
                resource_id=str(config.id)
            )
            
            return DiscordConfigResponse.from_orm(config)
        
        @self.router.delete("/{config_id}")
        async def delete_discord_config(
            config_id: int,
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Hapus konfigurasi Discord"""
            from app.domains.discord.services.discord_config_service import discord_config_service
            
            success = discord_config_service.delete_config(db, config_id)
            
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Konfigurasi Discord tidak ditemukan"
                )
            
            # Log audit
            from app.domains.admin.repositories.admin_repository import AuditLogRepository
            audit_repo = AuditLogRepository(db)
            audit_repo.create_log(
                admin_id=current_admin.id,
                action="DELETE",
                resource="discord_config",
                resource_id=str(config_id)
            )
            
            return APIResponse.success(message="Konfigurasi Discord berhasil dihapus")
        
        @self.router.post("/{config_id}/activate", response_model=DiscordConfigResponse)
        async def activate_discord_config(
            config_id: int,
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Aktifkan konfigurasi Discord"""
            from app.domains.discord.services.discord_config_service import discord_config_service
            from app.domains.discord.schemas.discord_config_schemas import DiscordConfigUpdate as OriginalDiscordConfigUpdate
            
            # Update config to active
            config_data = OriginalDiscordConfigUpdate(is_active=True)
            config = discord_config_service.update_config(db, config_id, config_data)
            
            if not config:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Konfigurasi Discord tidak ditemukan"
                )
            
            # Log audit
            from app.domains.admin.repositories.admin_repository import AuditLogRepository
            audit_repo = AuditLogRepository(db)
            audit_repo.create_log(
                admin_id=current_admin.id,
                action="ACTIVATE",
                resource="discord_config",
                resource_id=str(config.id)
            )
            
            return DiscordConfigResponse.from_orm(config)


# Main router yang menggabungkan semua controller
router = APIRouter()

# Initialize controllers
auth_controller = AdminAuthController()
admin_controller = AdminManagementController()
config_controller = ConfigurationController()
user_controller = UserManagementController()
product_controller = ProductManagementController()
dashboard_controller = DashboardController()
margin_controller = MarginManagementController()
discord_config_controller = DiscordConfigController()

# Include all routes
router.include_router(auth_controller.router, prefix="/auth", tags=["Admin Auth"])
router.include_router(admin_controller.router, prefix="/admins", tags=["Admin Management"])
router.include_router(config_controller.router, prefix="/config", tags=["Configuration"])
router.include_router(user_controller.router, prefix="/users", tags=["User Management"])
router.include_router(product_controller.router, prefix="/products", tags=["Product Management"])
router.include_router(dashboard_controller.router, prefix="/dashboard", tags=["Dashboard"])
router.include_router(margin_controller.router, prefix="/margins", tags=["Margin Management"])
router.include_router(discord_config_controller.router, prefix="/discord-config", tags=["Discord Configuration"])

# Include Analytics endpoints for admin
try:
    from app.domains.analytics.controllers.analytics_controller import router as analytics_router
    router.include_router(analytics_router, prefix="/analytics", tags=["Admin Analytics"])
except ImportError:
    pass

# Include Transaction endpoints for admin
try:
    from app.domains.transaction.controllers.transaction_controller import router as transaction_router
    router.include_router(transaction_router, prefix="/transactions", tags=["Admin Transactions"])
except ImportError:
    pass


class DiscordAdminController:
    """
    Controller untuk Discord Admin - Single Responsibility: Discord admin endpoints
    """
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup routes untuk Discord admin"""
        
        @self.router.get("/logs", response_model=PaginatedDiscordLogsResponse)
        async def get_discord_logs(
            page: int = 1,
            limit: int = 10,
            level: Optional[str] = None,
            action: Optional[str] = None,
            bot_id: Optional[int] = None,
            user_id: Optional[int] = None,
            guild_id: Optional[str] = None,
            channel_id: Optional[str] = None,
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil Discord logs dengan filter"""
            from app.domains.discord.services.discord_admin_service import DiscordAdminService
            from app.domains.discord.schemas.discord_admin_schemas import DiscordLogFilter
            
            # Create filter
            filters = DiscordLogFilter(
                level=level,
                action=action,
                bot_id=bot_id,
                user_id=user_id,
                guild_id=guild_id,
                channel_id=channel_id
            )
            
            discord_service = DiscordAdminService(db)
            result = discord_service.get_discord_logs(page, limit, filters)
            
            # Log audit
            from app.domains.admin.repositories.admin_repository import AuditLogRepository
            audit_repo = AuditLogRepository(db)
            audit_repo.create_log(
                admin_id=current_admin.id,
                action="VIEW",
                resource="discord_logs",
                resource_id=None,
                new_values=f"Viewed Discord logs page {page}"
            )
            
            return result
        
        @self.router.get("/commands/recent", response_model=List[DiscordCommandResponse])
        async def get_recent_discord_commands(
            limit: int = 5,
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil recent Discord commands"""
            from app.domains.discord.services.discord_admin_service import DiscordAdminService
            
            discord_service = DiscordAdminService(db)
            result = discord_service.get_recent_discord_commands(limit)
            
            # Log audit
            from app.domains.admin.repositories.admin_repository import AuditLogRepository
            audit_repo = AuditLogRepository(db)
            audit_repo.create_log(
                admin_id=current_admin.id,
                action="VIEW",
                resource="discord_commands",
                resource_id=None,
                new_values=f"Viewed recent Discord commands (limit: {limit})"
            )
            
            return result
        
        @self.router.get("/commands", response_model=PaginatedDiscordCommandsResponse)
        async def get_discord_commands(
            page: int = 1,
            limit: int = 5,
            command_name: Optional[str] = None,
            success: Optional[bool] = None,
            user_id: Optional[int] = None,
            guild_id: Optional[str] = None,
            channel_id: Optional[str] = None,
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil Discord commands dengan filter"""
            from app.domains.discord.services.discord_admin_service import DiscordAdminService
            from app.domains.discord.schemas.discord_admin_schemas import DiscordCommandFilter
            
            # Create filter
            filters = DiscordCommandFilter(
                command_name=command_name,
                success=success,
                user_id=user_id,
                guild_id=guild_id,
                channel_id=channel_id
            )
            
            discord_service = DiscordAdminService(db)
            result = discord_service.get_discord_commands(page, limit, filters)
            
            # Log audit
            from app.domains.admin.repositories.admin_repository import AuditLogRepository
            audit_repo = AuditLogRepository(db)
            audit_repo.create_log(
                admin_id=current_admin.id,
                action="VIEW",
                resource="discord_commands",
                resource_id=None,
                new_values=f"Viewed Discord commands page {page}"
            )
            
            return result
        
        @self.router.get("/stats", response_model=DiscordStatsResponse)
        async def get_discord_stats(
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil statistik Discord"""
            from app.domains.discord.services.discord_admin_service import DiscordAdminService
            
            discord_service = DiscordAdminService(db)
            result = discord_service.get_discord_stats()
            
            # Log audit
            from app.domains.admin.repositories.admin_repository import AuditLogRepository
            audit_repo = AuditLogRepository(db)
            audit_repo.create_log(
                admin_id=current_admin.id,
                action="VIEW",
                resource="discord_stats",
                resource_id=None,
                new_values="Viewed Discord statistics"
            )
            
            return result


# Initialize Discord admin controller
discord_admin_controller = DiscordAdminController()

# Include Discord admin routes
router.include_router(discord_admin_controller.router, prefix="/discord", tags=["Discord Admin"])
