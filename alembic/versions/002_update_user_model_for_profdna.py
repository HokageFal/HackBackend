"""update user model for profdna

Revision ID: 002_update_user_model
Revises: 001_initial_clean
Create Date: 2026-03-20 22:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002_update_user_model'
down_revision: Union[str, Sequence[str], None] = '001_initial_clean'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Создаем enum для ролей
    op.execute("CREATE TYPE userroleenum AS ENUM ('admin', 'psychologist')")
    
    # Добавляем новые колонки как nullable
    op.add_column('users', sa.Column('full_name', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('phone', sa.String(length=50), nullable=True))
    op.add_column('users', sa.Column('photo_url', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('role', postgresql.ENUM('admin', 'psychologist', name='userroleenum', create_type=False), nullable=True))
    op.add_column('users', sa.Column('about_markdown', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('public_card_token', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('access_until', sa.Date(), nullable=True))
    op.add_column('users', sa.Column('is_blocked', sa.Boolean(), nullable=True))
    
    # Заполняем данные для существующих пользователей
    op.execute("""
        UPDATE users 
        SET 
            full_name = COALESCE(username, 'Unknown User'),
            phone = '+00000000000',
            role = CASE WHEN is_admin THEN 'admin'::userroleenum ELSE 'psychologist'::userroleenum END,
            is_blocked = false
        WHERE full_name IS NULL
    """)
    
    # Теперь делаем колонки NOT NULL
    op.alter_column('users', 'full_name', nullable=False)
    op.alter_column('users', 'phone', nullable=False)
    op.alter_column('users', 'role', nullable=False)
    op.alter_column('users', 'is_blocked', nullable=False)
    
    # Остальные изменения
    op.alter_column('users', 'email', existing_type=sa.VARCHAR(length=255), nullable=False)
    op.alter_column('users', 'password', existing_type=sa.VARCHAR(length=255), nullable=False)
    op.create_unique_constraint('uq_users_public_card_token', 'users', ['public_card_token'])
    
    # Удаляем старые колонки
    op.drop_column('users', 'email_verified')
    op.drop_column('users', 'username')
    op.drop_column('users', 'avatar_url')
    
    # Удаляем старый enum auth_provider (если существует)
    op.execute("DROP TYPE IF EXISTS authproviderenum CASCADE")


def downgrade() -> None:
    """Downgrade schema."""
    # Восстанавливаем старые колонки
    op.execute("CREATE TYPE authproviderenum AS ENUM ('email')")
    op.add_column('users', sa.Column('auth_provider', postgresql.ENUM('email', name='authproviderenum'), nullable=False, server_default='email'))
    op.add_column('users', sa.Column('avatar_url', sa.TEXT(), nullable=True))
    op.add_column('users', sa.Column('username', sa.VARCHAR(length=255), nullable=False, server_default='user'))
    op.add_column('users', sa.Column('email_verified', sa.BOOLEAN(), nullable=False, server_default='false'))
    
    # Удаляем новые колонки
    op.drop_constraint('uq_users_public_card_token', 'users', type_='unique')
    op.alter_column('users', 'password', existing_type=sa.VARCHAR(length=255), nullable=True)
    op.alter_column('users', 'email', existing_type=sa.VARCHAR(length=255), nullable=True)
    op.drop_column('users', 'is_blocked')
    op.drop_column('users', 'access_until')
    op.drop_column('users', 'public_card_token')
    op.drop_column('users', 'about_markdown')
    op.drop_column('users', 'role')
    op.drop_column('users', 'photo_url')
    op.drop_column('users', 'phone')
    op.drop_column('users', 'full_name')
    
    # Удаляем enum ролей
    op.execute("DROP TYPE IF EXISTS userroleenum CASCADE")
