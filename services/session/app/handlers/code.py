from fastapi import APIRouter, Query
from uuid import UUID
from app.schemas.session import CodeUpdate, CodeResponse, CodeHistoryResponse

router = APIRouter(prefix="/sessions/{session_id}/code", tags=["Code"])


@router.get("/", response_model=CodeResponse)
async def get_current_code(session_id: UUID):
    """Получить текущий код кандидата"""
    pass


@router.put("/", response_model=CodeResponse)
async def update_code(session_id: UUID, code_data: CodeUpdate):
    """Обновить код кандидата (сохраняет новую версию)"""
    pass


@router.get("/versions", response_model=CodeHistoryResponse)
async def get_code_history(
    session_id: UUID,
    limit: int = Query(50, ge=1, le=500),
    skip: int = Query(0, ge=0),
):
    """Получить историю версий кода"""
    pass


@router.get("/versions/{version}", response_model=dict)
async def get_code_version(session_id: UUID, version: int):
    """Получить конкретную версию кода"""
    pass


@router.post("/reset")
async def reset_code(session_id: UUID):
    """Сбросить код к начальному состоянию"""
    pass