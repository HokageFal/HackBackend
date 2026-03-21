"""add datetime to profilefieldtype enum

Revision ID: 004
Revises: 003
Create Date: 2026-03-21 15:20:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Добавляем новое значение в enum
    op.execute("ALTER TYPE profilefieldtype ADD VALUE IF NOT EXISTS 'datetime'")


def downgrade() -> None:
    # PostgreSQL не поддерживает удаление значений из enum
    # Нужно пересоздавать enum, что сложно
    pass
