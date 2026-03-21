"""add datetime to profile values

Revision ID: 003
Revises: b017b6dfe701
Create Date: 2026-03-21 15:15:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003'
down_revision = 'b017b6dfe701'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Добавляем колонку datetime_value
    op.add_column('test_attempt_profile_values', 
        sa.Column('datetime_value', sa.DateTime(), nullable=True)
    )


def downgrade() -> None:
    # Удаляем колонку datetime_value
    op.drop_column('test_attempt_profile_values', 'datetime_value')
