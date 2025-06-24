from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.domains.admin.services.user_management_service import UserManagementService
from app.common.dependencies.admin_auth_deps import get_current_admin
from app.domains.admin.models.admin import Admin
from app.common.responses.api_response import APIResponse

logger = logging.getLogger(__name__)


class UserStatsController:
    """
    Controller untuk statistik user - Single Responsibility: User statistics
    """
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup routes untuk statistik user"""
        
        @self.router.get("/stats")
        async def get_user_stats(
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil statistik user"""
            user_service = UserManagementService(db)
            
            stats = user_service.get_user_stats()
            
            return APIResponse.success(data=stats)


# Initialize controller
user_stats_controller = UserStatsController()
