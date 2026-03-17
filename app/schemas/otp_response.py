from pydantic import BaseModel, Field


class OTPSentResponse(BaseModel):
    """Схема ответа при успешной отправке OTP кода."""
    message: str
    email: str
    expires_in_seconds: int = Field(
        description="Время жизни кода в секундах"
    )


class OTPVerifiedResponse(BaseModel):
    """Схема ответа при успешной проверке OTP кода."""
    message: str
    email: str
    verified: bool = True
