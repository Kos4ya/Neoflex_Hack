from uuid import UUID
from fastapi import APIRouter, status, Depends, HTTPException

from .base import get_room_service
from ..services.room_service import RoomService
from ..schemas.rooms import CodeCreate, CodeUpdate, CodeResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ..schemas.code import UpdateCurrentCodeRequest, CurrentCodeResponse
from ..database.session import get_db


router = APIRouter(prefix="/rooms", tags=["Code Editor"])


@router.get("/{room_id}/codes", response_model=list[CodeResponse])
async def get_room_codes(
    room_id: UUID,
    service: RoomService = Depends(get_room_service),
):
    """Получить все сохраненные версии кода комнаты"""
    room = await service.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    codes = await service.get_room_codes(room_id)
    return codes


@router.post("/{room_id}/codes", response_model=CodeResponse, status_code=status.HTTP_201_CREATED)
async def create_code(
    room_id: UUID,
    code_data: CodeCreate,
    service: RoomService = Depends(get_room_service),
):
    """Сохранить новую версию кода"""
    code = await service.create_code(room_id, code_data)
    if not code:
        raise HTTPException(status_code=404, detail="Room not found")

    await service.db.commit()
    await service.db.refresh(code)
    return code


@router.put("/codes/{code_id}", response_model=CodeResponse)
async def update_code(
    code_id: UUID,
    code_data: CodeUpdate,
    service: RoomService = Depends(get_room_service),
):
    """Обновить существующую версию кода"""
    code = await service.update_code(code_id, code_data)
    if not code:
        raise HTTPException(status_code=404, detail="Code not found")

    await service.db.commit()
    await service.db.refresh(code)
    return code


@router.delete("/codes/{code_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_code(
    code_id: UUID,
    service: RoomService = Depends(get_room_service),
):
    """Удалить версию кода"""
    deleted = await service.delete_code(code_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Code not found")
    await service.db.commit()


@router.get("/{room_id}/code/current")
async def get_current_code(room_id: UUID, db: AsyncSession = Depends(get_db)):
    service = RoomService(db)

    room = await service.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    code = await service.get_current_code(room_id)

    if not code:
        return CurrentCodeResponse(
            room_id=str(room_id),
            code_body="",
            version=0,
        )

    return CurrentCodeResponse(
        room_id=str(room_id),
        code_body=code.code_body,
        version=code.version,
    )


@router.put("/{room_id}/code/current")
async def put_current_code(
    room_id: UUID,
    payload: UpdateCurrentCodeRequest,
    db: AsyncSession = Depends(get_db),
):
    service = RoomService(db)

    try:
        code = await service.upsert_current_code(
            room_id=room_id,
            code_body=payload.code_body,
            version=payload.version,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    await db.commit()
    await db.refresh(code)

    return CurrentCodeResponse(
        room_id=str(room_id),
        code_body=code.code_body,
        version=code.version,
    )