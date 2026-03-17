"""
Документация ответов для GitHub OAuth эндпоинтов.

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
# GITHUB LOGIN RESPONSES
# =============================================================================

GITHUB_LOGIN_SUCCESS = {
    302: {
        "description": "Перенаправление на страницу авторизации GitHub",
        "content": {
            "text/html": {
                "example": "Redirect to GitHub OAuth authorization page"
            }
        }
    }
}

GITHUB_LOGIN_SERVER_ERROR = {
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

# Объединенные responses для GitHub login
GITHUB_LOGIN_RESPONSES = {
    **GITHUB_LOGIN_SUCCESS,
    **GITHUB_LOGIN_SERVER_ERROR,
}

# =============================================================================
# GITHUB CALLBACK RESPONSES
# =============================================================================

GITHUB_CALLBACK_SUCCESS = {
    200: {
        "model": AuthSuccessResponse,
        "description": "Успешная аутентификация через GitHub OAuth",
        "content": {
            "application/json": {
                "example": {
                    "status": "success",
                    "message": "Вход через GitHub выполнен успешно",
                    "data": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer",
                        "user": {
                            "id": 123,
                            "username": "testuser",
                            "email": "test@example.com",
                            "avatar_url": "https://avatars.githubusercontent.com/u/123456?v=4"
                        }
                    },
                    "errors": None
                }
            }
        }
    }
}

GITHUB_CALLBACK_OAUTH_ERROR = {
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
                                    "field": "oauth_error",
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
                                    "field": "oauth_error",
                                    "message": "invalid_request: Invalid OAuth request parameters",
                                    "input": None,
                                    "ctx": {
                                        "reason": "Invalid OAuth request"
                                    }
                                }
                            ]
                        }
                    },
                    "no_verified_email": {
                        "summary": "У GitHub аккаунта нет подтвержденной почты",
                        "value": {
                            "status": "error",
                            "message": "Ошибка бизнес-логики",
                            "data": None,
                            "errors": [
                                {
                                    "type": "business_error",
                                    "field": "email",
                                    "message": "У вашего GitHub аккаунта нет подтвержденной почты",
                                    "input": None,
                                    "ctx": {
                                        "reason": "No verified email found on GitHub"
                                    }
                                }
                            ]
                        }
                    },
                    "no_user_profile": {
                        "summary": "Не удалось получить профиль GitHub",
                        "value": {
                            "status": "error",
                            "message": "Ошибка бизнес-логики",
                            "data": None,
                            "errors": [
                                {
                                    "type": "business_error",
                                    "field": "user_profile",
                                    "message": "Не удалось получить профиль GitHub",
                                    "input": None,
                                    "ctx": {
                                        "reason": "GitHub user profile is empty"
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

GITHUB_CALLBACK_SERVER_ERROR = {
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

# Объединенные responses для GitHub callback
GITHUB_CALLBACK_RESPONSES = {
    **GITHUB_CALLBACK_SUCCESS,
    **GITHUB_CALLBACK_OAUTH_ERROR,
    **GITHUB_CALLBACK_SERVER_ERROR,
}