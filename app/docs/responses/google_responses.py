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
# GOOGLE LOGIN RESPONSES
# =============================================================================

GOOGLE_LOGIN_SUCCESS = {
    302: {
        "description": "Перенаправление на страницу авторизации Google",
        "content": {
            "text/html": {
                "example": "Redirect to Google OAuth authorization page"
            }
        }
    }
}

GOOGLE_LOGIN_SERVER_ERROR = {
    500: {
        "model": ErrorResponse,
        "description": "Серверная ошибка при инициации OAuth",
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

# Объединенные responses для Google login
GOOGLE_LOGIN_RESPONSES = {
    **GOOGLE_LOGIN_SUCCESS,
    **GOOGLE_LOGIN_SERVER_ERROR,
}

# =============================================================================
# GOOGLE CALLBACK RESPONSES
# =============================================================================

GOOGLE_CALLBACK_SUCCESS = {
    200: {
        "model": AuthSuccessResponse,
        "description": "Успешная аутентификация через Google OAuth",
        "content": {
            "application/json": {
                "example": {
                    "status": "success",
                    "message": "Вход через Google выполнен успешно",
                    "data": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer",
                        "user": {
                            "id": 123,
                            "username": "testuser",
                            "email": "test@example.com",
                            "avatar_url": "https://lh3.googleusercontent.com/a/default-user"
                        }
                    },
                    "errors": None
                }
            }
        }
    }
}

GOOGLE_CALLBACK_OAUTH_ERROR = {
    400: {
        "model": ErrorResponse,
        "description": "Ошибка OAuth авторизации",
        "content": {
            "application/json": {
                "examples": {
                    "oauth_denied": {
                        "summary": "Пользователь отклонил авторизацию",
                        "value": {
                            "status": "error",
                            "message": "Ошибка бизнес-логики",
                            "data": None,
                            "errors": [
                                {
                                    "type": "business_error",
                                    "field": "oauth_code",
                                    "message": "access_denied: The user denied the request",
                                    "input": None,
                                    "ctx": {
                                        "reason": "OAuth authorization denied"
                                    }
                                }
                            ]
                        }
                    },
                    "invalid_request": {
                        "summary": "Неверный OAuth запрос",
                        "value": {
                            "status": "error",
                            "message": "Ошибка бизнес-логики",
                            "data": None,
                            "errors": [
                                {
                                    "type": "business_error",
                                    "field": "oauth_code",
                                    "message": "invalid_request: Invalid OAuth request parameters",
                                    "input": None,
                                    "ctx": {
                                        "reason": "Invalid OAuth request"
                                    }
                                }
                            ]
                        }
                    },
                    "no_user_info": {
                        "summary": "Не удалось получить информацию о пользователе",
                        "value": {
                            "status": "error",
                            "message": "Ошибка бизнес-логики",
                            "data": None,
                            "errors": [
                                {
                                    "type": "business_error",
                                    "field": "user_info",
                                    "message": "Не удалось получить информацию о пользователе от Google",
                                    "input": None,
                                    "ctx": {
                                        "reason": "No user info received"
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

GOOGLE_CALLBACK_SERVER_ERROR = {
    500: {
        "model": ErrorResponse,
        "description": "Серверная ошибка при обработке OAuth callback",
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

# Объединенные responses для Google callback
GOOGLE_CALLBACK_RESPONSES = {
    **GOOGLE_CALLBACK_SUCCESS,
    **GOOGLE_CALLBACK_OAUTH_ERROR,
    **GOOGLE_CALLBACK_SERVER_ERROR,
}