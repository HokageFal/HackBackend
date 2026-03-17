"""
Унифицированные схемы ответов API.

Все ответы API должны следовать единому формату:
{
    "status": "success" | "error",
    "message": "Описание результата операции",
    "data": { /* любая полезная нагрузка */ },
    "errors": [
        {
            "type": "value_error" | "missing" | "server_error" | "conflict" | "...",
            "field": "username" | "password" | "email" | null,
            "message": "Детальное сообщение об ошибке",
            "input": {}, // значение, которое вызвало ошибку (если есть)
            "ctx": { "reason": "Код/текст причины" } // дополнительные данные
        }
    ]
}
"""

from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional, Union, Literal


class ApiError(BaseModel):
    """
    Модель для описания отдельной ошибки в API ответе.
    """
    type: str = Field(
        ...,
        description="Тип ошибки",
        examples=["value_error", "missing", "server_error", "conflict", "not_found", "unauthorized"]
    )
    field: Optional[str] = Field(
        None,
        description="Поле, связанное с ошибкой",
        examples=["username", "password", "email"]
    )
    message: str = Field(
        ...,
        description="Детальное сообщение об ошибке"
    )
    input: Optional[Any] = Field(
        None,
        description="Значение, которое вызвало ошибку"
    )
    ctx: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Дополнительные данные об ошибке"
    )


class ApiResponse(BaseModel):
    """
    Базовая модель для всех API ответов.
    """
    status: Literal["success", "error"] = Field(
        ...,
        description="Статус операции"
    )
    message: str = Field(
        ...,
        description="Описание результата операции"
    )
    data: Optional[Dict[str, Any]] = Field(
        None,
        description="Полезная нагрузка ответа"
    )
    errors: Optional[List[ApiError]] = Field(
        None,
        description="Список ошибок (только для status='error')"
    )

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "status": "success",
                    "message": "Операция выполнена успешно",
                    "data": {"id": 123, "name": "example"},
                    "errors": None
                },
                {
                    "status": "error",
                    "message": "Ошибка валидации данных",
                    "data": None,
                    "errors": [
                        {
                            "type": "value_error",
                            "field": "email",
                            "message": "Некорректный формат email адреса",
                            "input": "invalid-email",
                            "ctx": {"reason": "Invalid email format"}
                        }
                    ]
                }
            ]
        }


class SuccessResponse(ApiResponse):
    """
    Модель для успешных ответов API.
    """
    status: Literal["success"] = "success"
    errors: None = None


class ErrorResponse(ApiResponse):
    """
    Модель для ответов с ошибками API.
    """
    status: Literal["error"] = "error"
    data: None = None
    errors: List[ApiError] = Field(
        ...,
        min_items=1,
        description="Список ошибок"
    )


# Специализированные модели для конкретных типов ответов

class AuthSuccessResponse(SuccessResponse):
    """
    Модель для успешных ответов аутентификации.
    """
    data: Dict[str, Any] = Field(
        ...,
        description="Данные аутентификации (токены, информация о пользователе)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Вход выполнен успешно",
                "data": {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "bearer",
                    "user": {
                        "id": 123,
                        "username": "testuser",
                        "email": "test@example.com"
                    }
                },
                "errors": None
            }
        }


class UserDataResponse(SuccessResponse):
    """
    Модель для ответов с данными пользователя.
    """
    data: Dict[str, Any] = Field(
        ...,
        description="Данные пользователя"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Данные пользователя получены успешно",
                "data": {
                    "id": 123,
                    "username": "testuser",
                    "email": "test@example.com",
                    "avatar_url": "https://example.com/avatar.jpg",
                    "is_admin": False,
                    "created_at": "2024-01-15T10:30:00Z",
                    "updated_at": "2024-01-15T10:30:00Z"
                },
                "errors": None
            }
        }


class OtpResponse(SuccessResponse):
    """
    Модель для ответов OTP операций.
    """
    data: Dict[str, Any] = Field(
        ...,
        description="Данные OTP операции"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Код подтверждения отправлен на email",
                "data": {
                    "email": "user@example.com",
                    "expires_in_seconds": 600,
                    "verified": True
                },
                "errors": None
            }
        }