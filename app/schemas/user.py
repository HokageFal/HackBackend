from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr = Field(
        description="Корректный email адрес"
    )
    password: str = Field(
        min_length=8,
        max_length=100,
        description="Пароль от 8 до 100 символов"
    )
    
    # Простая валидация - только длина пароля (активна по умолчанию)
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
