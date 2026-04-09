# database/session.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator
from uuid import uuid4
from sqlalchemy import select

from ..config import settings

Base = declarative_base()

_engine = None
_async_sessionmaker = None


async def init_database():
    """Инициализация подключения к базе данных"""
    global _engine, _async_sessionmaker

    _engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=3600,
    )

    _async_sessionmaker = async_sessionmaker(
        _engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    # Создаем таблицы
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Инициализируем начальные данные
    await init_initial_data()


async def init_initial_data():
    """Инициализация начальных данных в БД"""
    from ..models.metric import Metric  # Импортируем здесь, чтобы избежать циклических импортов

    INITIAL_METRICS = [
        {"name": "Решение задач", "scale_from": 0, "scale_to": 10, "visible": True},
        {"name": "Качество кода", "scale_from": 0, "scale_to": 10, "visible": True},
        {"name": "Коммуникация", "scale_from": 0, "scale_to": 10, "visible": True},
        {"name": "Системное мышление", "scale_from": 0, "scale_to": 10, "visible": True},
        {"name": "Отладка", "scale_from": 0, "scale_to": 10, "visible": True},
    ]

    async with _async_sessionmaker() as session:
        # Проверяем, есть ли уже метрики в БД
        result = await session.execute(select(Metric))
        existing_metrics = result.scalars().all()

        if existing_metrics:
            print(f"📊 Метрики уже существуют в БД ({len(existing_metrics)} шт.)")
            return

        # Добавляем начальные метрики
        metrics_to_add = []
        for metric_data in INITIAL_METRICS:
            metric = Metric(
                id=uuid4(),
                name=metric_data["name"],
                scale_from=metric_data["scale_from"],
                scale_to=metric_data["scale_to"],
                visible=metric_data["visible"]
            )
            metrics_to_add.append(metric)

        session.add_all(metrics_to_add)
        await session.commit()

        print(f"✅ Добавлено {len(metrics_to_add)} начальных метрик в БД")
        for metric in metrics_to_add:
            print(f"  - {metric.name} (scale: {metric.scale_from}-{metric.scale_to})")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with _async_sessionmaker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def close_database():
    """Закрытие соединения с БД (при остановке приложения)"""
    global _engine
    if _engine:
        await _engine.dispose()


def get_engine():
    return _engine


def get_sessionmaker():
    return _async_sessionmaker