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
    
    # Простая валидация - только длина пароля (активна по умолчанию)
    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Пароль должен содержать минимум 8 символов")
        return v
    
    # Полная валидация пароля (раскомментируйте для строгой проверки)
    # @field_validator("password")
    # @classmethod
    # def validate_password(cls, v: str) -> str:
    #     if len(v) < 8:
    #         raise ValueError("Пароль должен содержать минимум 8 символов")
    #     if not any(c.isupper() for c in v):
    #         raise ValueError("Пароль должен содержать хотя бы одну заглавную букву")
    #     if not any(c.islower() for c in v):
    #         raise ValueError("Пароль должен содержать хотя бы одну строчную букву")
    #     if not any(c.isdigit() for c in v):
    #         raise ValueError("Пароль должен содержать хотя бы одну цифру")
    #     return v
