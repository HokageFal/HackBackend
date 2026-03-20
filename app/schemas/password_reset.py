from pydantic import BaseModel, EmailStr, Field, field_validator


class PasswordResetRequest(BaseModel):
    """Запрос на сброс пароля."""
    email: EmailStr = Field(..., description="Email пользователя")


class PasswordResetVerify(BaseModel):
    """Подтверждение сброса пароля с новым паролем."""
    email: EmailStr = Field(..., description="Email пользователя")
    code: str = Field(..., min_length=6, max_length=6, description="6-значный код подтверждения")
    new_password: str = Field(..., min_length=8, max_length=72, description="Новый пароль")
    
    
    # Простая валидация (как при регистрации) - только длина пароля
    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Пароль должен содержать минимум 8 символов")
        return v
    
    # Полная валидация пароля (раскомментируйте для строгой проверки, закомментировав простую валидацию выше)
    # @field_validator("new_password")
    # @classmethod
    # def validate_password_full(cls, v: str) -> str:
    #     if len(v) < 8:
    #         raise ValueError("Пароль должен содержать минимум 8 символов")
    #     if not any(c.isupper() for c in v):
    #         raise ValueError("Пароль должен содержать хотя бы одну заглавную букву")
    #     if not any(c.islower() for c in v):
    #         raise ValueError("Пароль должен содержать хотя бы одну строчную букву")
    #     if not any(c.isdigit() for c in v):
    #         raise ValueError("Пароль должен содержать хотя бы одну цифру")
    #     return v
