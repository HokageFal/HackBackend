from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional

class UserCreate(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=50,
        description="Имя пользователя от 3 до 50 символов"
    )
    email: EmailStr = Field(
        description="Корректный email адрес"
    )
    password: str = Field(
        min_length=8,
        max_length=100,
        description="Пароль от 8 до 100 символов"
    )
    avatar_url: Optional[str] = Field(
        default=None,
        max_length=500,
        description="URL аватара (максимум 500 символов)"
    )
    email_verified: bool = Field(
        default=False,
        description="Статус подтверждения email"
    )
