from typing import Generator, Annotated, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session
from app.services.file_watcher import FileWatcherService
from app.core.config import settings
from app.core import security
from app.core.database import get_db

# Try to import User from domains
try:
    from app.domains.auth.models.user import User
except ImportError:
    User = None

# Try to import services
try:
    from app.services.auth_service import AuthService
except ImportError:
    AuthService = None

# Try to import schemas
try:
    from app.schemas.auth import TokenData
except ImportError:
    TokenData = None

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

def get_file_watcher() -> Generator[FileWatcherService, None, None]:
    try:
        service = FileWatcherService(settings.WATCH_PATH)
        yield service
    finally:
        service.stop()

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db)
):
    """Dependency untuk mendapatkan user yang sedang login"""
    if not User or not AuthService or not TokenData:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Authentication not available"
        )
    
    auth_service = AuthService(db)
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = security.verify_token(token)
        if payload is None:
            raise credentials_exception
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = auth_service.get_user_by_username(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: Annotated[dict, Depends(get_current_user)]
):
    """Dependency untuk mendapatkan user yang sedang aktif"""
    if not hasattr(current_user, 'is_active') or not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user

async def get_current_superuser(
    current_user: Annotated[dict, Depends(get_current_active_user)]
):
    """Dependency untuk mendapatkan superuser"""
    if not hasattr(current_user, 'is_superuser') or not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    return current_user
