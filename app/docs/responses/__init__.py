"""
Модуль с документацией ответов API.

Содержит унифицированные схемы ответов для всех эндпоинтов API,
следующие единому формату проекта.
"""

from .user_responses import (
    USER_LOGIN_RESPONSES,
    REFRESH_TOKEN_RESPONSES,
    ACCESS_TOKEN_RESPONSES,
    USER_BY_ID_RESPONSES
)

__all__ = [
    # User responses
    "USER_LOGIN_RESPONSES",
    "REFRESH_TOKEN_RESPONSES",
    "ACCESS_TOKEN_RESPONSES",
    "USER_BY_ID_RESPONSES",
]