from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import create_access_token, create_refresh_token, verify_token
from app.services.auth_service import AuthService
from app.schemas.auth import UserCreate, UserResponse, Token, RefreshToken, UserUpdate
from app.api.deps import get_current_active_user
from app.models.user import User
from app.utils.responses import create_success_response, create_error_response

router = APIRouter()

@router.post("/register", response_model=dict)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Registrasi user baru"""
    try:
        auth_service = AuthService(db)
        user = auth_service.create_user(user_data)
        
        return create_success_response(
            message="User berhasil didaftarkan",
            data=UserResponse.from_orm(user)
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal mendaftarkan user: {str(e)}"
        )

@router.post("/login", response_model=dict)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
):
    """Login user"""
    try:
        auth_service = AuthService(db)
        user = auth_service.authenticate_user(form_data.username, form_data.password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Username atau password salah",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Buat tokens
        access_token = create_access_token(data={"sub": user.username})
        refresh_token = create_refresh_token(data={"sub": user.username})
        
        token_data = Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )
        
        return create_success_response(
            message="Login berhasil",
            data=token_data
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal login: {str(e)}"
        )

@router.post("/refresh", response_model=dict)
async def refresh_token(
    refresh_data: RefreshToken,
    db: Session = Depends(get_db)
):
    """Refresh access token"""
    try:
        # Verify refresh token
        payload = verify_token(refresh_data.refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        username = payload.get("sub")
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Verify user exists
        auth_service = AuthService(db)
        user = auth_service.get_user_by_username(username)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new access token
        access_token = create_access_token(data={"sub": user.username})
        
        return create_success_response(
            message="Token berhasil diperbarui",
            data={"access_token": access_token, "token_type": "bearer"}
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal refresh token: {str(e)}"
        )

@router.get("/me", response_model=dict)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    """Ambil informasi user yang sedang login"""
    return create_success_response(
        message="Informasi user berhasil diambil",
        data=UserResponse.from_orm(current_user)
    )

@router.put("/me", response_model=dict)
async def update_current_user(
    user_data: UserUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db)
):
    """Update informasi user yang sedang login"""
    try:
        auth_service = AuthService(db)
        updated_user = auth_service.update_user(current_user.id, user_data)
        
        return create_success_response(
            message="Informasi user berhasil diperbarui",
            data=UserResponse.from_orm(updated_user)
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal update user: {str(e)}"
        )
