from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, TIMESTAMP, Enum, func, Text, Boolean, Date
from app.database.core import Base
import enum
from datetime import date


class UserRoleEnum(str, enum.Enum):
    admin = "admin"
    psychologist = "psychologist"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(String(50), nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    photo_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(
        TIMESTAMP, server_default=func.now(), nullable=False
    )
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Поля для ролей и управления доступом
    role: Mapped[UserRoleEnum] = mapped_column(
        Enum(UserRoleEnum), default=UserRoleEnum.psychologist, nullable=False
    )
    about_markdown: Mapped[str | None] = mapped_column(Text, nullable=True)
    public_card_token: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True)
    access_until: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
