from fastapi import APIRouter, Query, status
from typing import List, Optional
from app.schemas.user import UserCreate, UserUpdate, UserResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=List[UserResponse])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
):
    """Список пользователей"""
    pass


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """Получение пользователя по ID"""
    pass


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate):
    """Создание пользователя"""
    pass


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, user_data: UserUpdate):
    """Обновление пользователя"""
    pass


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str):
    """Удаление пользователя"""
    pass


@router.patch("/{user_id}/role")
async def change_user_role(user_id: str, role: str):
    """Смена роли пользователя"""
    pass