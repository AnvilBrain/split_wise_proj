import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from settings import settings

# 1. URL для подключения (например, к PostgreSQL через драйвер asyncpg)
DATABASE_URL = settings.DATABASE_URL

# 2. Создание асинхронного Engine (управляет пулом подключений)
engine = create_async_engine(
    DATABASE_URL,
    echo=True,          # Логирует все SQL-запросы в консоль (удобно для отладки)
    pool_size=20,       # Максимальное количество постоянных подключений
    max_overflow=10     # Дополнительные подключения, если пул переполнен
)

# 3. Фабрика для генерации сессий (AsyncSession)
# expire_on_commit=False предотвращает ошибку DetachedInstanceError при обращении к данным после коммита
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)


    
# 4. Базовый класс для ORM-моделей
Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session