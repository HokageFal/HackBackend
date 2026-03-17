"""
Документация ответов для пользовательских эндпоинтов.

Все ответы следуют унифицированному формату API:
{
    "status": "success" | "error",
    "message": "Описание результата операции",
    "data": { /* полезная нагрузка */ },
    "errors": [{ /* детали ошибок */ }]
}
"""

from app.schemas.api_response import (
    ErrorResponse, 
    SuccessResponse, 
    AuthSuccessResponse, 
    UserDataResponse
)

# =============================================================================
# USER REGISTER RESPONSES
# =============================================================================

USER_REGISTER_SUCCESS = {
    201: {
        "model": SuccessResponse,
        "description": "Пользователь успешно зарегистрирован",
        "content": {
            "application/json": {
                "example": {
                    "status": "success",
                    "message": "Регистрация прошла успешно",
                    "data": {
                        "user_id": 52,
                        "email": "user@example.com",
                        "username": "testuser"
                    },
                    "errors": None
                }
            }
        },
    }
}

USER_REGISTER_BUSINESS_ERROR = {
    400: {
        "model": ErrorResponse,
        "description": "Ошибка бизнес-логики",
        "content": {
            "application/json": {
                "example": {
                    "status": "error",
                    "message": "Ошибка бизнес-логики",
                    "data": None,
                    "errors": [
                        {
                            "type": "business_error",
                            "field": None,
                            "message": "Некорректные данные для регистрации",
                            "input": None,
                            "ctx": {"reason": "Invalid registration data"}
                        }
                    ]
                }
            },
        },
    }
}

USER_REGISTER_CONFLICT_ERROR = {
    409: {
        "model": ErrorResponse,
        "description": "Email или username занят",
        "content": {
            "application/json": {
                "example": {
                    "status": "error",
                    "message": "Конфликт данных",
                    "data": None,
                    "errors": [
                        {
                            "type": "conflict",
                            "field": "email",
                            "message": "Пользователь с таким email уже существует",
                            "input": "existing@email.com",
                            "ctx": {"reason": "Email already exists"}
                        }
                    ]
                }
            }
        },
    }
}

USER_REGISTER_FORBIDDEN_ERROR = {
    403: {
        "model": ErrorResponse,
        "description": "Email не подтвержден",
        "content": {
            "application/json": {
                "example": {
                    "status": "error",
                    "message": "Доступ запрещен",
                    "data": None,
                    "errors": [
                        {
                            "type": "forbidden",
                            "field": "email",
                            "message": "Проверьте почту для подтверждения email",
                            "input": "unverified@email.com",
                            "ctx": {"reason": "Email not verified"}
                        }
                    ]
                }
            },
        },
    }
}

USER_REGISTER_VALIDATION_ERROR = {
    422: {
        "model": ErrorResponse,
        "description": "Ошибка валидации",
        "content": {
            "application/json": {
                "example": {
                    "detail": [
                        {
                            "type": "missing",
                            "loc": ["body", "password"],
                            "msg": "Поле обязательно для заполнения",
                            "input": {"username": "test", "email": "test@example.com"}
                        }
                    ]
                }
            },
        },
    }
}

USER_REGISTER_SERVER_ERROR = {
    500: {
        "model": ErrorResponse,
        "description": "Серверная ошибка",
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
                            "ctx": {"reason": "Internal server error"}
                        }
                    ]
                }
            },
        },
    }
}

USER_REGISTER_RESPONSES = {
    **USER_REGISTER_SUCCESS,
    **USER_REGISTER_BUSINESS_ERROR,
    **USER_REGISTER_CONFLICT_ERROR,
    **USER_REGISTER_FORBIDDEN_ERROR,
    **USER_REGISTER_VALIDATION_ERROR,
    **USER_REGISTER_SERVER_ERROR,
}

# =============================================================================
# USER LOGIN RESPONSES
# =============================================================================

USER_LOGIN_SUCCESS = {
    200: {
        "model": AuthSuccessResponse,
        "description": "Успешный вход",
        "content": {
            "application/json": {
                "example": {
                    "status": "success",
                    "message": "Вход выполнен успешно",
                    "data": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer",
                        "user": {
                            "id": 1,
                            "username": "john_doe",
                            "email": "john@example.com",
                            "avatar_url": "https://example.com/avatar.jpg",
                            "is_admin": False
                        }
                    },
                    "errors": None
                }
            }
        }
    }
}

USER_LOGIN_AUTH_ERROR = {
    401: {
        "model": ErrorResponse,
        "description": "Неверный email или пароль",
        "content": {
            "application/json": {
                "example": {
                    "status": "error",
                    "message": "Ошибка аутентификации",
                    "data": None,
                    "errors": [
                        {
                            "type": "unauthorized",
                            "field": "email",
                            "message": "Пользователь с таким email не найден",
                            "input": "nonexistent@email.com",
                            "ctx": {"reason": "Authentication failed for email"}
                        }
                    ]
                }
            },
        },
    }
}

USER_LOGIN_FORBIDDEN_ERROR = {
    403: {
        "model": ErrorResponse,
        "description": "Email не подтвержден",
        "content": {
            "application/json": {
                "example": {
                    "status": "error",
                    "message": "Доступ запрещен",
                    "data": None,
                    "errors": [
                        {
                            "type": "forbidden",
                            "field": "email",
                            "message": "Email не подтвержден. Проверьте почту",
                            "input": "unverified@email.com",
                            "ctx": {"reason": "Email not verified"}
                        }
                    ]
                }
            },
        },
    }
}

USER_LOGIN_VALIDATION_ERROR = {
    422: {
        "model": ErrorResponse,
        "description": "Ошибка валидации",
        "content": {
            "application/json": {
                "example": {
                    "detail": [
                        {
                            "type": "missing",
                            "loc": ["body", "password"],
                            "msg": "Поле обязательно для заполнения",
                            "input": {"email": "user@example.com"}
                        }
                    ]
                }
            }
        },
    }
}

USER_LOGIN_SERVER_ERROR = {
    500: {
        "model": ErrorResponse,
        "description": "Серверная ошибка",
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
                            "message": "Сервер временно недоступен",
                            "input": None,
                            "ctx": {"reason": "Internal server error"}
                        }
                    ]
                }
            }
        }
    }
}

USER_LOGIN_RESPONSES = {
    **USER_LOGIN_SUCCESS,
    **USER_LOGIN_AUTH_ERROR,
    **USER_LOGIN_FORBIDDEN_ERROR,
    **USER_LOGIN_VALIDATION_ERROR,
    **USER_LOGIN_SERVER_ERROR,
}

# =============================================================================
# REFRESH TOKEN RESPONSES
# =============================================================================

REFRESH_TOKEN_SUCCESS = {
    200: {
        "model": AuthSuccessResponse,
        "description": "Access токен обновлен",
        "content": {
            "application/json": {
                "example": {
                    "status": "success",
                    "message": "Токен успешно обновлен",
                    "data": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer"
                    },
                    "errors": None
                }
            }
        }
    }
}

REFRESH_TOKEN_AUTH_ERROR = {
    401: {
        "model": ErrorResponse,
        "description": "Невалидный refresh токен",
        "content": {
            "application/json": {
                "example": {
                    "status": "error",
                    "message": "Ошибка аутентификации",
                    "data": None,
                    "errors": [
                        {
                            "type": "unauthorized",
                            "field": "cookie",
                            "message": "Refresh токен не найден в куках",
                            "input": "***",
                            "ctx": {"reason": "Authentication failed for cookie"}
                        }
                    ]
                }
            },
        },
    }
}

REFRESH_TOKEN_CSRF_ERROR = {
    403: {
        "model": ErrorResponse,
        "description": "CSRF токен невалиден",
        "content": {
            "application/json": {
                "example": {
                    "status": "error",
                    "message": "Доступ запрещен",
                    "data": None,
                    "errors": [
                        {
                            "type": "forbidden",
                            "field": "csrf_token",
                            "message": "CSRF токен отсутствует или невалиден",
                            "input": None,
                            "ctx": {"reason": "Access forbidden for csrf_token"}
                        }
                    ]
                }
            }
        }
    }
}

REFRESH_TOKEN_SERVER_ERROR = {
    500: {
        "model": ErrorResponse,
        "description": "Серверная ошибка",
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
                            "message": "Сервер временно недоступен",
                            "input": None,
                            "ctx": {"reason": "Internal server error"}
                        }
                    ]
                }
            },
        },
    }
}

REFRESH_TOKEN_RESPONSES = {
    **REFRESH_TOKEN_SUCCESS,
    **REFRESH_TOKEN_AUTH_ERROR,
    **REFRESH_TOKEN_CSRF_ERROR,
    **REFRESH_TOKEN_SERVER_ERROR,
}

# =============================================================================
# ACCESS TOKEN VERIFICATION RESPONSES
# =============================================================================

ACCESS_TOKEN_SUCCESS = {
    200: {
        "model": SuccessResponse,
        "description": "Пользователь авторизован",
        "content": {
            "application/json": {
                "example": {
                    "status": "success",
                    "message": "Пользователь авторизован",
                    "data": {"authorized": True},
                    "errors": None
                }
            }
        }
    }
}

ACCESS_TOKEN_NOT_FOUND_ERROR = {
    404: {
        "model": ErrorResponse,
        "description": "Access токен не найден",
        "content": {
            "application/json": {
                "example": {
                    "status": "error",
                    "message": "Ресурс не найден",
                    "data": None,
                    "errors": [
                        {
                            "type": "not_found",
                            "field": "Authorization",
                            "message": "Токен не найден в заголовке Authorization",
                            "input": None,
                            "ctx": {"reason": "Authorization not found"}
                        }
                    ]
                }
            },
        },
    }
}

ACCESS_TOKEN_AUTH_ERROR = {
    401: {
        "model": ErrorResponse,
        "description": "Невалидный access токен",
        "content": {
            "application/json": {
                "example": {
                    "status": "error",
                    "message": "Ошибка аутентификации",
                    "data": None,
                    "errors": [
                        {
                            "type": "unauthorized",
                            "field": "token",
                            "message": "Access токен истек",
                            "input": "***",
                            "ctx": {"reason": "Authentication failed for token"}
                        }
                    ]
                }
            },
        },
    }
}

ACCESS_TOKEN_SERVER_ERROR = {
    500: {
        "model": ErrorResponse,
        "description": "Серверная ошибка",
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
                            "message": "Сервер временно недоступен",
                            "input": None,
                            "ctx": {"reason": "Internal server error"}
                        }
                    ]
                }
            },
        },
    }
}

ACCESS_TOKEN_RESPONSES = {
    **ACCESS_TOKEN_SUCCESS,
    **ACCESS_TOKEN_NOT_FOUND_ERROR,
    **ACCESS_TOKEN_AUTH_ERROR,
    **ACCESS_TOKEN_SERVER_ERROR,
}

# =============================================================================
# USER BY ID RESPONSES
# =============================================================================

USER_BY_ID_SUCCESS = {
    200: {
        "model": UserDataResponse,
        "description": "Данные пользователя получены",
        "content": {
            "application/json": {
                "example": {
                    "status": "success",
                    "message": "Данные пользователя получены успешно",
                    "data": {
                        "id": 1,
                        "username": "john_doe",
                        "email": "john@example.com",
                        "avatar_url": "https://example.com/avatar.jpg",
                        "is_admin": False,
                        "created_at": "2024-01-15T10:30:00",
                        "token_balance": 0
                    },
                    "errors": None
                }
            }
        }
    }
}

USER_BY_ID_NOT_FOUND_ERROR = {
    404: {
        "model": ErrorResponse,
        "description": "Пользователь не найден",
        "content": {
            "application/json": {
                "example": {
                    "status": "error",
                    "message": "Ресурс не найден",
                    "data": None,
                    "errors": [
                        {
                            "type": "not_found",
                            "field": "user_id",
                            "message": "Пользователь не найден",
                            "input": 999,
                            "ctx": {"reason": "user_id not found"}
                        }
                    ]
                }
            },
        },
    }
}

USER_BY_ID_SERVER_ERROR = {
    500: {
        "model": ErrorResponse,
        "description": "Серверная ошибка",
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
                            "message": "Сервер временно недоступен",
                            "input": None,
                            "ctx": {"reason": "Internal server error"}
                        }
                    ]
                }
            },
        },
    }
}

USER_BY_ID_RESPONSES = {
    **USER_BY_ID_SUCCESS,
    **USER_BY_ID_NOT_FOUND_ERROR,
    **ACCESS_TOKEN_AUTH_ERROR,
    **ACCESS_TOKEN_SERVER_ERROR,
}

# =============================================================================
# USER DELETE RESPONSES
# =============================================================================

USER_DELETE_SUCCESS = {
    200: {
        "model": SuccessResponse,
        "description": "Пользователь успешно удален",
        "content": {
            "application/json": {
                "example": {
                    "status": "success",
                    "message": "Пользователь успешно удален",
                    "data": {"user_id": 1},
                    "errors": None
                }
            }
        }
    }
}

USER_DELETE_RESPONSES = {
    **USER_DELETE_SUCCESS,
    **USER_BY_ID_NOT_FOUND_ERROR,
    **ACCESS_TOKEN_AUTH_ERROR,
    **ACCESS_TOKEN_SERVER_ERROR,
}

# =============================================================================
# USER UPDATE PROFILE RESPONSES
# =============================================================================

USER_UPDATE_PROFILE_SUCCESS = {
    200: {
        "model": UserDataResponse,
        "description": "Профиль обновлен",
        "content": {
            "application/json": {
                "example": {
                    "status": "success",
                    "message": "Профиль успешно обновлен",
                    "data": {
                        "id": 1,
                        "username": "new_username",
                        "email": "john@example.com",
                        "avatar_url": "https://example.com/new_avatar.jpg",
                        "is_admin": False,
                        "created_at": "2024-01-15T10:30:00"
                    },
                    "errors": None
                }
            }
        }
    }
}

USER_UPDATE_PROFILE_RESPONSES = {
    **USER_UPDATE_PROFILE_SUCCESS,
    **USER_BY_ID_NOT_FOUND_ERROR,
    **ACCESS_TOKEN_AUTH_ERROR,
    **ACCESS_TOKEN_SERVER_ERROR,
}


# =============================================================================
# USER LOGOUT RESPONSES
# =============================================================================

USER_LOGOUT_SUCCESS = {
    200: {
        "model": SuccessResponse,
        "description": "Пользователь успешно вышел из системы",
        "content": {
            "application/json": {
                "example": {
                    "status": "success",
                    "message": "Выход выполнен успешно",
                    "data": None,
                    "errors": None
                }
            }
        },
        "headers": {
            "Set-Cookie": {
                "description": "Refresh токен удаляется из cookies",
                "schema": {
                    "type": "string",
                    "example": "jwt=; Max-Age=0; Path=/; HttpOnly; Secure; SameSite=Strict"
                }
            }
        }
    }
}

USER_LOGOUT_RESPONSES = {
    **USER_LOGOUT_SUCCESS,
}
