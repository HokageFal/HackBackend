"""
Модуль с документацией ответов API.

Содержит унифицированные схемы ответов для всех эндпоинтов API,
следующие единому формату проекта.
"""

from .user_responses import (
    USER_REGISTER_RESPONSES,
    USER_LOGIN_RESPONSES,
    REFRESH_TOKEN_RESPONSES,
    ACCESS_TOKEN_RESPONSES,
    USER_BY_ID_RESPONSES
)

from .otp_responses import (
    OTP_SEND_RESPONSES,
    OTP_VERIFY_RESPONSES
)

__all__ = [
    # User responses
    "USER_REGISTER_RESPONSES",
    "USER_LOGIN_RESPONSES",
    "REFRESH_TOKEN_RESPONSES",
    "ACCESS_TOKEN_RESPONSES",
    "USER_BY_ID_RESPONSES",
    
    # OTP responses
    "OTP_SEND_RESPONSES",
    "OTP_VERIFY_RESPONSES",
]