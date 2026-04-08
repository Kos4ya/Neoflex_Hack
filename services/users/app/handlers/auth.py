from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from ..services.auth_services import AuthService
from app.schemas.user import (
    UserRegister, UserLogin, UserResponse
)
from app.schemas.auth import (
    TokenResponse,
    RefreshTokenRequest
)
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/get_token", response_model=TokenResponse)
async def get_token(
        credentials: UserLogin,
        db: AsyncSession = Depends(get_db),
):
    auth_service = AuthService(db)

    try:
        tokens = await auth_service.login(credentials)
        return tokens
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
        user_data: UserRegister,
        db: AsyncSession = Depends(get_db),
):
    """Регистрация нового пользователя"""
    auth_service = AuthService(db)

    existing = await auth_service.user_service.get_user_by_email(user_data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )

    try:
        tokens = await auth_service.register(user_data)
        return tokens
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/login", response_model=TokenResponse)
async def login(
        credentials: UserLogin,
        db: AsyncSession = Depends(get_db),
):
    """Вход в систему"""
    auth_service = AuthService(db)

    try:
        tokens = await auth_service.login(credentials)
        return tokens
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.post("/logout")
async def logout(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
):
    """Выход из системы"""
    auth_service = AuthService(db)
    await auth_service.logout(current_user.id)
    return {"message": "Logged out successfully"}


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
        request: RefreshTokenRequest,
        db: AsyncSession = Depends(get_db),
):
    """Обновление access токена"""
    auth_service = AuthService(db)

    try:
        tokens = await auth_service.refresh_access_token(request.refresh_token)
        return tokens
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
        current_user: User = Depends(get_current_user),
):
    """Получить текущего пользователя"""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        department=current_user.department,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        last_login=current_user.last_login,
    )
