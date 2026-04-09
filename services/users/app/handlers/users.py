from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID

from app.database.session import get_db
from app.services.user_service import UserService
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserRole
from app.dependencies.auth import get_current_manager, get_current_user
from app.models.user import User

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=List[UserResponse])
async def list_users(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=500),
        role: Optional[UserRole] = None,
        is_active: Optional[bool] = None,
        current_user: User = Depends(get_current_manager),
        db: AsyncSession = Depends(get_db),
):
    """Список пользователей (только для менеджеров+)"""
    user_service = UserService(db)
    users = await user_service.list_users(
        skip=skip,
        limit=limit,
        role=role,
        is_active=is_active,
    )

    return [
        UserResponse(
            id=u.id,
            email=u.email,
            full_name=u.full_name,
            role=u.role,
            department=u.department,
            is_active=u.is_active,
            created_at=u.created_at,
            last_login=u.last_login,
        )
        for u in users
    ]


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
        user_id: UUID,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
):
    """Получение пользователя по ID"""
    user_service = UserService(db)
    user = await user_service.get_user_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        department=user.department,
        is_active=user.is_active,
        created_at=user.created_at,
        last_login=user.last_login,
    )


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
        user_data: UserCreate,
        current_user: User = Depends(get_current_manager),
        db: AsyncSession = Depends(get_db),
):
    """Создание пользователя (только для менеджеров+)"""
    user_service = UserService(db)

    existing = await user_service.get_user_by_email(user_data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )

    user = await user_service.create_user(user_data)
    await db.commit()

    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        department=user.department,
        is_active=user.is_active,
        created_at=user.created_at,
        last_login=user.last_login,
    )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
        user_id: UUID,
        user_data: UserUpdate,
        current_user: User = Depends(get_current_manager),
        db: AsyncSession = Depends(get_db),
):
    """Обновление пользователя (только для менеджеров+)"""
    user_service = UserService(db)

    user = await user_service.update_user(user_id, user_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    await db.commit()

    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        department=user.department,
        is_active=user.is_active,
        created_at=user.created_at,
        last_login=user.last_login,
    )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
        user_id: UUID,
        current_user: User = Depends(get_current_manager),
        db: AsyncSession = Depends(get_db),
):
    """Удаление пользователя (мягкое) (только для менеджеров+)"""
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account",
        )

    user_service = UserService(db)
    success = await user_service.delete_user(user_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    await db.commit()


@router.patch("/{user_id}/role")
async def change_user_role(
        user_id: UUID,
        role: UserRole,
        current_user: User = Depends(get_current_manager),
        db: AsyncSession = Depends(get_db),
):
    """Смена роли пользователя (только для менеджеров+)"""
    user_service = UserService(db)
    user = await user_service.get_user_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    user.role = role
    await db.commit()

    return {
        "message": "Role changed successfully",
        "user_id": str(user_id),
        "new_role": role.value,
    }