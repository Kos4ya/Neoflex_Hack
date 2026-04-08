from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from uuid import UUID
from typing import Optional
from enum import Enum


class UserRole(str, Enum):
    """Роли пользователей"""
    INTERVIEWER = "interviewer"
    MANAGER = "manager"
    ADMIN = "admin"


class UserBase(BaseModel):
    """Базовые поля пользователя"""
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=255)
    department: Optional[str] = Field(None, max_length=100)


class UserCreate(UserBase):
    """Создание пользователя"""
    password: str = Field(..., min_length=6)
    role: UserRole = UserRole.INTERVIEWER

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v


class UserUpdate(BaseModel):
    """Обновление пользователя (все поля опциональны)"""
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    department: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None


class UserRegister(UserCreate):
    """Регистрация пользователя (совпадает с UserCreate)"""
    pass


class UserResponse(UserBase):
    """Ответ с данными пользователя"""
    id: UUID
    role: UserRole
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """Логин пользователя"""
    email: EmailStr
    password: str


class ChangePasswordRequest(BaseModel):
    """Смена пароля"""
    old_password: str
    new_password: str = Field(..., min_length=6)

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v
