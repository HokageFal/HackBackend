import asyncio
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine

# Загружаем Base и модели
from app.database.core import Base
from app.database.models.users import User
from app.database.models.subscription_plans import SubscriptionPlan
from app.database.models.user_subscriptions import UserSubscription
from app.database.models.token_ledger import TokenTransaction

# Загружаем переменные окружения из .env
from dotenv import load_dotenv
load_dotenv()

# -------------------------------------------------
# Alembic Config
# -------------------------------------------------
config = context.config

# Настройка логирования Alembic (из alembic.ini)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Основная метаинформация для автогенерации миграций
target_metadata = Base.metadata


# -------------------------------------------------
# Конфигурируем URL базы
# -------------------------------------------------
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@db:5432/postgres"
)

# Для async engine заменяем psycopg2 на asyncpg
if DATABASE_URL and "psycopg2" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("psycopg2", "asyncpg")


# -------------------------------------------------
# Offline migrations
# -------------------------------------------------
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


# -------------------------------------------------
# Online migrations (async)
# -------------------------------------------------
def do_run_migrations(connection):
    """Sync wrapper around migration execution."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = create_async_engine(
        DATABASE_URL,
        echo=True,  # можно выключить логирование SQL при желании
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


# -------------------------------------------------
# Entrypoint
# -------------------------------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
