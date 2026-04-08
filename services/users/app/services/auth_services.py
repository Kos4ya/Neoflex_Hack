from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
from uuid import UUID, uuid4

from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.schemas.user import UserLogin, UserCreate
from app.services.user_service import UserService
from ..core.secure import (
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)


class AuthService:
    """Сервис для аутентификации и работы с токенами"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_service = UserService(db)

    async def register(self, user_data: UserCreate) -> Dict[str, Any]:
        """Регистрация нового пользователя"""
        user = await self.user_service.create_user(user_data)
        await self.db.commit()

        return await self._create_tokens(user)

    async def login(self, credentials: UserLogin) -> Dict[str, Any]:
        """Вход пользователя в систему"""
        user = await self.user_service.get_user_by_email(credentials.email)

        if not user:
            raise ValueError("Invalid email or password")

        if not verify_password(credentials.password, user.password_hash):
            raise ValueError("Invalid email or password")

        if not user.is_active:
            raise ValueError("User account is disabled")

        # Обновляем время последнего входа
        await self.user_service.update_last_login(user.id)
        await self.db.commit()

        return await self._create_tokens(user)

    async def _create_tokens(self, user: User) -> Dict[str, Any]:
        """Создает access и refresh токены для пользователя"""
        access_token = create_access_token({
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value,
        })

        refresh_token = create_refresh_token({"sub": str(user.id)})

        refresh_token_obj = RefreshToken(
            user_id=user.id,
            token=refresh_token,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        )
        self.db.add(refresh_token_obj)
        await self.db.commit()

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 1800,  # 30 минут в секундах
        }

    async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """Обновляет access токен по refresh токену"""
        result = await self.db.execute(
            select(RefreshToken).where(
                RefreshToken.token == refresh_token,
                RefreshToken.revoked == False
            )
        )
        db_refresh = result.scalar_one_or_none()

        if not db_refresh:
            raise ValueError("Invalid refresh token")

        if db_refresh.expires_at < datetime.now(timezone.utc):
            raise ValueError("Refresh token expired")

        user = await self.user_service.get_user_by_id(db_refresh.user_id)
        if not user or not user.is_active:
            raise ValueError("User not found or inactive")

        db_refresh.revoked = True

        return await self._create_tokens(user)

    async def logout(self, user_id: UUID) -> None:
        """Выход из системы - отзываем все refresh токены пользователя"""
        await self.db.execute(
            delete(RefreshToken).where(RefreshToken.user_id == user_id)
        )
        await self.db.commit()

    async def get_current_user(self, token: str) -> Optional[User]:
        """Получает текущего пользователя по access токену"""
        payload = decode_token(token)

        if not payload:
            return None

        # Проверяем тип токена
        if payload.get("type") != "access":
            return None

        user_id = payload.get("sub")
        if not user_id:
            return None

        user = await self.user_service.get_user_by_id(UUID(user_id))
        return user

    async def validate_token_for_service(self, token: str) -> Dict[str, Any]:
        """Валидация токена для других микросервисов (Internal API)"""
        payload = decode_token(token)

        if not payload:
            return {"valid": False, "error": "Invalid token"}

        if payload.get("type") != "access":
            return {"valid": False, "error": "Not an access token"}

        user_id = payload.get("sub")
        if not user_id:
            return {"valid": False, "error": "No user_id in token"}

        user = await self.user_service.get_user_by_id(UUID(user_id))
        if not user:
            return {"valid": False, "error": "User not found"}

        if not user.is_active:
            return {"valid": False, "error": "User is inactive"}

        return {
            "valid": True,
            "user_id": str(user.id),
            "email": user.email,
            "role": user.role.value,
        }