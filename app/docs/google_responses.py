"""
Документация ответов для Google OAuth эндпоинтов.

Все ответы следуют унифицированному формату API:
{
    "status": "success" | "error",
    "message": "Описание результата операции",
    "data": { /* полезная нагрузка */ },
    "errors": [{ /* детали ошибок */ }]
}
"""

from app.schemas.api_response import ErrorResponse, AuthSuccessResponse

# =============================================================================
# GOOGLE AUTH RESPONSES (POST /users/auth/google)
# =============================================================================

GOOGLE_AUTH_SUCCESS = {
    200: {
        "model": AuthSuccessResponse,
        "description": "Успешная аутентификация через Google OAuth",
        "content": {
            "application/json": {
                "example": {
                    "status": "success",
                    "message": "Вход через Google выполнен успешно",
                    "data": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwidHlwZSI6ImFjY2VzcyIsImlzX2FkbWluIjpmYWxzZSwiaWF0IjoxNzA0NDU2MDAwLCJleHAiOjE3MDQ0NTYwNjB9...",
                        "token_type": "bearer",
                        "user": {
                            "id": 1,
                            "username": "John Doe",
                            "email": "john@gmail.com",
                            "avatar_url": "https://lh3.googleusercontent.com/a/ACg8ocK..."
                        }
                    },
                    "errors": None
                }
            }
        },
        "headers": {
            "Set-Cookie": {
                "description": "Refresh токен устанавливается в httpOnly cookie",
                "schema": {
                    "type": "string",
                    "example": "jwt=<refresh_token>; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=1296000"
                }
            }
        }
    }
}

GOOGLE_AUTH_VALIDATION_ERROR = {
    422: {
        "model": ErrorResponse,
        "description": "Ошибка валидации входных данных",
        "content": {
            "application/json": {
                "examples": {
                    "missing_token": {
                        "summary": "Отсутствует токен",
                        "value": {
                            "status": "error",
                            "message": "Ошибка валидации данных",
                            "data": None,
                            "errors": [
                                {
                                    "type": "validation_error",
                                    "field": "token",
                                    "message": "Поле обязательно для заполнения",
                                    "input": None,
                                    "ctx": {
                                        "reason": "Field required"
                                    }
                                }
                            ]
                        }
                    },
                    "invalid_token_format": {
                        "summary": "Неверный формат токена",
                        "value": {
                            "status": "error",
                            "message": "Ошибка валидации данных",
                            "data": None,
                            "errors": [
                                {
                                    "type": "validation_error",
                                    "field": "token",
                                    "message": "Строка должна содержать минимум 1 символов",
                                    "input": "",
                                    "ctx": {
                                        "reason": "String too short"
                                    }
                                }
                            ]
                        }
                    }
                }
            }
        }
    }
}

GOOGLE_AUTH_BUSINESS_ERROR = {
    400: {
        "model": ErrorResponse,
        "description": "Ошибка бизнес-логики при обработке Google токена",
        "content": {
            "application/json": {
                "examples": {
                    "invalid_token": {
                        "summary": "Не удалось верифицировать токен",
                        "value": {
                            "status": "error",
                            "message": "Ошибка бизнес-логики",
                            "data": None,
                            "errors": [
                                {
                                    "type": "business_error",
                                    "field": "token",
                                    "message": "Не удалось верифицировать токен Google",
                                    "input": None,
                                    "ctx": {
                                        "reason": "Token used too late"
                                    }
                                }
                            ]
                        }
                    },
                    "invalid_audience": {
                        "summary": "Неверный audience в токене",
                        "value": {
                            "status": "error",
                            "message": "Ошибка бизнес-логики",
                            "data": None,
                            "errors": [
                                {
                                    "type": "business_error",
                                    "field": "token",
                                    "message": "Неверный токен Google",
                                    "input": None,
                                    "ctx": {
                                        "reason": "Invalid audience"
                                    }
                                }
                            ]
                        }
                    },
                    "expired_token": {
                        "summary": "Токен истек",
                        "value": {
                            "status": "error",
                            "message": "Ошибка бизнес-логики",
                            "data": None,
                            "errors": [
                                {
                                    "type": "business_error",
                                    "field": "token",
                                    "message": "Не удалось верифицировать токен Google",
                                    "input": None,
                                    "ctx": {
                                        "reason": "Token expired"
                                    }
                                }
                            ]
                        }
                    }
                }
            }
        }
    }
}

GOOGLE_AUTH_SERVER_ERROR = {
    500: {
        "model": ErrorResponse,
        "description": "Серверная ошибка при обработке Google авторизации",
        "content": {
            "application/json": {
                "example": {
                    "status": "error",
                    "message": "Внутренняя ошибка сервера",
                    "data": None,
                    "errors": [
                        {
                            "type": "server_error",
                            "field": None,
                            "message": "Сервер временно недоступен. Попробуйте позже.",
                            "input": None,
                            "ctx": {
                                "reason": "Internal server error"
                            }
                        }
                    ]
                }
            }
        }
    }
}

# Объединенные responses для Google auth
GOOGLE_AUTH_RESPONSES = {
    **GOOGLE_AUTH_SUCCESS,
    **GOOGLE_AUTH_VALIDATION_ERROR,
    **GOOGLE_AUTH_BUSINESS_ERROR,
    **GOOGLE_AUTH_SERVER_ERROR,
}

# Для обратной совместимости (если где-то используется старое название)
GOOGLE_CALLBACK_RESPONSES = GOOGLE_AUTH_RESPONSES
