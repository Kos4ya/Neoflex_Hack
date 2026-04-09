from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from uuid import UUID

from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate
from app.core.secure import hash_password


class UserService:
    """Сервис для работы с пользователями"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Получить пользователя по ID"""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Получить пользователя по email"""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def create_user(self, user_data: UserCreate) -> User:
        """Создать нового пользователя"""
        user = User(
            email=user_data.email,
            password_hash=hash_password(user_data.password),
            full_name=user_data.full_name,
            role=user_data.role,
            department=user_data.department,
        )
        self.db.add(user)
        await self.db.flush()
        return user

    async def update_user(self, user_id: UUID, user_data: UserUpdate) -> Optional[User]:
        """Обновить данные пользователя"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return None

        if user_data.full_name is not None:
            user.full_name = user_data.full_name
        if user_data.department is not None:
            user.department = user_data.department
        if user_data.is_active is not None:
            user.is_active = user_data.is_active

        await self.db.flush()
        return user

    async def list_users(
            self,
            skip: int = 0,
            limit: int = 100,
            role: Optional[UserRole] = None,
            is_active: Optional[bool] = None,
    ) -> List[User]:
        """Получить список пользователей с фильтрацией"""
        query = select(User)

        if role:
            query = query.where(User.role == role)
        if is_active is not None:
            query = query.where(User.is_active == is_active)

        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def delete_user(self, user_id: UUID) -> bool:
        """Мягкое удаление пользователя (деактивация)"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return False

        user.is_active = False
        await self.db.flush()
        return True

    async def activate_user(self, user_id: UUID) -> bool:
        """Активация пользователя"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return False

        user.is_active = True
        await self.db.flush()
        return True

    async def update_last_login(self, user_id: UUID) -> None:
        """Обновить время последнего входа"""
        user = await self.get_user_by_id(user_id)
        if user:
            from datetime import datetime, timezone
            user.last_login = datetime.now(timezone.utc)
            await self.db.flush()
