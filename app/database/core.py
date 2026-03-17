import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Асинхронный движок
engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

SYNC_DATABASE_URL = DATABASE_URL.replace(
    "postgresql+asyncpg",
    "postgresql+psycopg2"
)
sync_engine = create_engine(SYNC_DATABASE_URL, echo=False)

SessionLocalSync = sessionmaker(
    bind=sync_engine,
    autoflush=False,
    autocommit=False
)

# Базовый класс для моделей
class Base(DeclarativeBase):
    pass

# Зависимость для FastAPI
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

