from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator
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

    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


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