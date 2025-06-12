from typing import List
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.shared.base_classes.base_controller import BaseController
from app.shared.responses.api_response import APIResponse
from app.domains.auth.services.auth_service import AuthService
from app.domains.auth.repositories.user_repository import UserRepository
from app.domains.auth.models.user import User
from app.domains.auth.schemas.auth_schemas import (
    UserCreate, UserUpdate, UserResponse, UserLogin, 
    Token, RefreshToken, PasswordChange, UserStats
)
from app.api.deps import get_db, get_current_user
from app.infrastructure.security.token_handler import TokenHandler

class AuthController(BaseController[User, AuthService, UserCreate, UserUpdate, UserResponse]):
    """
    Authentication controller yang mengimplementasikan Open/Closed Principle.
    Dapat di-extend untuk fitur authentication tambahan.
    """
    
    def __init__(self):
        # Dependency injection akan dilakukan melalui FastAPI
        super().__init__(None, "/auth", ["authentication"])
        self.token_handler = TokenHandler()
        self._setup_auth_routes()
    
    def _setup_auth_routes(self):
        """Setup routes khusus untuk authentication"""
        self.router.add_api_route(
            "/login",
            self.login,
            methods=["POST"],
            response_model=APIResponse[Token]
        )
        self.router.add_api_route(
            "/refresh",
            self.refresh_token,
            methods=["POST"],
            response_model=APIResponse[dict]
        )
        self.router.add_api_route(
            "/me",
            self.get_current_user_profile,
            methods=["GET"],
            response_model=APIResponse[UserResponse]
        )
        self.router.add_api_route(
            "/change-password",
            self.change_password,
            methods=["POST"],
            response_model=APIResponse[dict]
        )
        self.router.add_api_route(
            "/stats",
            self.get_user_stats,
            methods=["GET"],
            response_model=APIResponse[UserStats]
        )
    
    async def create_item(self, item_data: UserCreate, db: Session = Depends(get_db)) -> APIResponse[UserResponse]:
        """Registrasi user baru"""
        try:
            repository = UserRepository(db)
            service = AuthService(repository)
            
            user = service.create(item_data.dict())
            return APIResponse.success_response(
                data=UserResponse.from_orm(user),
                message="User berhasil didaftarkan"
            )
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def get_item(self, item_id: int, db: Session = Depends(get_db)) -> APIResponse[UserResponse]:
        """Ambil user berdasarkan ID"""
        try:
            repository = UserRepository(db)
            service = AuthService(repository)
            
            user = service.get_by_id(item_id)
            return APIResponse.success_response(
                data=UserResponse.from_orm(user),
                message="User berhasil diambil"
            )
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def get_items(self, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)) -> APIResponse[List[UserResponse]]:
        """Ambil semua users dengan pagination"""
        try:
            repository = UserRepository(db)
            service = AuthService(repository)
            
            users = service.get_all(skip, limit)
            total = repository.count_total_users()
            
            user_responses = [UserResponse.from_orm(user) for user in users]
            
            return APIResponse.paginated_response(
                data=user_responses,
                total=total,
                page=(skip // limit) + 1,
                per_page=limit,
                message="Users berhasil diambil"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def update_item(self, item_id: int, item_data: UserUpdate, db: Session = Depends(get_db)) -> APIResponse[UserResponse]:
        """Update user"""
        try:
            repository = UserRepository(db)
            service = AuthService(repository)
            
            user = service.update(item_id, item_data.dict(exclude_unset=True))
            return APIResponse.success_response(
                data=UserResponse.from_orm(user),
                message="User berhasil diupdate"
            )
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def delete_item(self, item_id: int, db: Session = Depends(get_db)) -> APIResponse[dict]:
        """Hapus user (soft delete)"""
        try:
            repository = UserRepository(db)
            service = AuthService(repository)
            
            success = service.delete(item_id)
            if success:
                return APIResponse.success_response(
                    data={"deleted": True},
                    message="User berhasil dihapus"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Gagal menghapus user"
                )
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def login(self, login_data: UserLogin, db: Session = Depends(get_db)) -> APIResponse[Token]:
        """Login user"""
        try:
            repository = UserRepository(db)
            service = AuthService(repository)
            
            user = service.authenticate_user(login_data.username, login_data.password)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Username atau password salah"
                )
            
            # Buat token
            user_data = {
                "sub": user.username,
                "user_id": user.id,
                "username": user.username
            }
            
            token_data = self.token_handler.create_token_pair(user_data)
            
            return APIResponse.success_response(
                data=Token(**token_data),
                message="Login berhasil"
            )
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def refresh_token(self, refresh_data: RefreshToken) -> APIResponse[dict]:
        """Refresh access token"""
        try:
            token_data = self.token_handler.refresh_access_token(refresh_data.refresh_token)
            return APIResponse.success_response(
                data=token_data,
                message="Token berhasil di-refresh"
            )
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def get_current_user_profile(self, current_user: User = Depends(get_current_user)) -> APIResponse[UserResponse]:
        """Ambil profil user yang sedang login"""
        return APIResponse.success_response(
            data=UserResponse.from_orm(current_user),
            message="Profil user berhasil diambil"
        )
    
    async def change_password(
        self, 
        password_data: PasswordChange, 
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> APIResponse[dict]:
        """Ubah password user"""
        try:
            repository = UserRepository(db)
            service = AuthService(repository)
            
            success = service.change_password(current_user.id, password_data)
            if success:
                return APIResponse.success_response(
                    data={"changed": True},
                    message="Password berhasil diubah"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Gagal mengubah password"
                )
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def get_user_stats(self, db: Session = Depends(get_db)) -> APIResponse[UserStats]:
        """Ambil statistik users"""
        try:
            repository = UserRepository(db)
            service = AuthService(repository)
            
            stats = service.get_user_stats()
            return APIResponse.success_response(
                data=UserStats(**stats),
                message="Statistik user berhasil diambil"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

# Instance controller
auth_controller = AuthController()
router = auth_controller.router
