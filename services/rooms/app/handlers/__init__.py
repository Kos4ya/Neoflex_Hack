"""Экспорт всех роутеров для включения в основное приложение"""

from .rooms import router as rooms_router
from .metrics import router as metrics_router
from .room_metrics import router as room_metrics_router
from .feedbacks import router as feedbacks_router
from .notes import router as notes_router
from .codes import router as codes_router
from .interviews import router as interviews_router

# Список всех роутеров для удобного импорта
all_routers = [
    rooms_router,
    metrics_router,
    room_metrics_router,
    feedbacks_router,
    notes_router,
    codes_router,
    interviews_router,
]
