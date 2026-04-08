# app/handlers/auth.py
from fastapi import APIRouter, status
from app.schemas.user import (
    UserRegister, UserLogin, TokenResponse,
    RefreshTokenRequest, UserResponse
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister):
    """Регистрация нового пользователя"""
    pass


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """Вход в систему"""
    pass


@router.post("/logout")
async def logout():
    """Выход из системы"""
    pass


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest):
    """Обновление access токена"""
    pass


@router.get("/me", response_model=UserResponse)
async def get_current_user():
    """Получить текущего пользователя"""
    pass