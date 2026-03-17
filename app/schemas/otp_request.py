from pydantic import BaseModel, EmailStr, Field


class OTPRequest(BaseModel):
    """Схема запроса OTP кода на email."""
    email: EmailStr = Field(
        description="Email адрес для отправки кода подтверждения"
    )


class OTPVerify(BaseModel):
    """Схема проверки OTP кода."""
    email: EmailStr = Field(
        description="Email адрес пользователя"
    )
    code: str = Field(
        min_length=6,
        max_length=6,
        description="6-значный код подтверждения"
    )
