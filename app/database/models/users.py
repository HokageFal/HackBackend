from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, TIMESTAMP, Enum, func, Text, Boolean
from app.database.core import Base  # твой Base
import enum


class AuthProviderEnum(str, enum.Enum):
    email = "email"
    google = "google"
    telegram = "telegram"
    github = "github"

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(255), nullable=False, unique=False)
    email: Mapped[str] = mapped_column(String(255), nullable=True, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    auth_provider: Mapped[AuthProviderEnum] = mapped_column(
        Enum(AuthProviderEnum), default=AuthProviderEnum.email, nullable=False
    )
    google_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    telegram_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    github_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    created_at: Mapped[str] = mapped_column(
        TIMESTAMP, server_default=func.now(), nullable=False
    )
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    token_balance: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
