from app.schemas.error_response import ErrorResponse

USER_REGISTER_SUCCESS = {
    201: {
        "description": "Пользователь успешно зарегистрирован",
        "content": {
            "application/json": {
                "example": {
                    "message": "Регистрация прошла успешно",
                    "user_id": 52
                }
            }
        },
    }
}

USER_REGISTER_BUSINESS_ERROR = {
    400: {
        "model": ErrorResponse,
        "description": "Ошибка бизнес-логики или пользовательская ошибка",
        "content": {
            "application/json": {
                "example": {
                    "detail": [
                        {
                            "type": "value_error",
                            "loc": ["body"],
                            "msg": "Некорректные данные для регистрации пользователя",
                            "input": {},
                            "ctx": {
                                "reason": "Invalid registration data"
                            }
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
                "examples": {
                    "email_exists": {
                        "summary": "Email уже зарегистрирован",
                        "value": {
                            "detail": [
                                {
                                    "type": "value_error",
                                    "loc": ["body", "email"],
                                    "msg": "Пользователь с таким email уже существует",
                                    "input": "existing@email.com",
                                    "ctx": {
                                        "reason": "Email already exists"
                                    }
                                }
                            ]
                        },
                    },
                }
            }
        },
    }
}

USER_REGISTER_FORBIDDEN_ERROR = {
    403: {
        "model": ErrorResponse,
        "description": "Email уже зарегистрирован, но не подтвержден",
        "content": {
            "application/json": {
                "example": {
                    "detail": [
                        {
                            "type": "forbidden",
                            "loc": ["body", "email"],
                            "msg": "Проверьте почту для подтверждения email",
                            "input": "unverified@email.com",
                            "ctx": {
                                "reason": "Email not verified"
                            }
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
        "description": "Ошибка валидации данных (FastAPI / Pydantic)",
        "content": {
            "application/json": {
                "examples": {
                    "missing_field": {
                        "summary": "Отсутствует обязательное поле",
                        "value": {
                            "detail": [
                                {
                                    "type": "missing",
                                    "loc": ["body", "password"],
                                    "msg": "Поле обязательно для заполнения",
                                    "input": {
                                        "username": "Grady Bode",
                                        "email": "Deshawn_Lang@hotmail.com",
                                        "avatar_url": "url"
                                    }
                                }
                            ]
                        },
                    },
                    "invalid_email_format": {
                        "summary": "Некорректный формат email",
                        "value": {
                            "detail": [
                                {
                                    "type": "value_error",
                                    "loc": ["body", "email"],
                                    "msg": "Некорректный формат email адреса: email должен содержать символ @",
                                    "input": "Deshawn_Langhotmail.com",
                                    "ctx": {
                                        "reason": "Email адрес должен содержать символ @"
                                    }
                                }
                            ]
                        },
                    },
                    "username_too_short": {
                        "summary": "Username слишком короткий",
                        "value": {
                            "detail": [
                                {
                                    "type": "string_too_short",
                                    "loc": ["body", "username"],
                                    "msg": "Имя пользователя должно содержать минимум 3 символа",
                                    "input": "ab",
                                    "ctx": {
                                        "min_length": 3
                                    }
                                }
                            ]
                        },
                    },
                    "username_too_long": {
                        "summary": "Username слишком длинный",
                        "value": {
                            "detail": [
                                {
                                    "type": "string_too_long",
                                    "loc": ["body", "username"],
                                    "msg": "Имя пользователя должно содержать максимум 50 символов",
                                    "input": "a" * 51,
                                    "ctx": {
                                        "max_length": 50
                                    }
                                }
                            ]
                        },
                    },
                    "password_too_short": {
                        "summary": "Пароль слишком короткий",
                        "value": {
                            "detail": [
                                {
                                    "type": "string_too_short",
                                    "loc": ["body", "password"],
                                    "msg": "Пароль должен содержать минимум 8 символов",
                                    "input": "1234567",
                                    "ctx": {
                                        "min_length": 8
                                    }
                                }
                            ]
                        },
                    },
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
                    "detail": [
                        {
                            "type": "server_error",
                            "loc": ["body"],
                            "msg": "Сервер временно недоступен. Попробуйте позже.",
                            "input": {},
                            "ctx": {
                                "reason": "Internal server error"
                            }
                        }
                    ]
                }
            },
        },
    }
}

# Объединенные responses для регистрации
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
        "description": "Успешный вход",
        "content": {
            "application/json": {
                "example": {
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
                    }
                }
            }
        },
        "headers": {
            "Set-Cookie": {
                "description": "Refresh токен и CSRF токен устанавливаются в httpOnly cookies",
                "schema": {
                    "type": "string",
                    "example": "jwt=<refresh_token>; HttpOnly; Secure; SameSite=Strict; csrf_token=<csrf_token>; HttpOnly; Secure; SameSite=Strict"
                }
            }
        }
    }
}

USER_LOGIN_BUSINESS_ERROR = {
    400: {
        "model": ErrorResponse,
        "description": "Ошибка бизнес-логики или пользовательская ошибка",
        "content": {
            "application/json": {
                "example": {
                    "detail": [
                        {
                            "type": "value_error",
                            "loc": ["body"],
                            "msg": "Некорректные данные для входа пользователя",
                            "input": {},
                            "ctx": {
                                "reason": "Invalid login data"
                            }
                        }
                    ]
                }
            },
        },
    }
}

USER_LOGIN_AUTH_ERROR = {
    401: {
        "model": ErrorResponse,
        "description": "Неверный email или пароль",
        "content": {
            "application/json": {
                "examples": {
                    "email_not_found": {
                        "summary": "Email не найден",
                        "value": {
                            "detail": [
                                {
                                    "type": "value_error",
                                    "loc": ["body", "email"],
                                    "msg": "Пользователь с таким email не найден",
                                    "input": "nonexistent@email.com",
                                    "ctx": {
                                        "reason": "User not found"
                                    }
                                }
                            ]
                        }
                    },
                    "wrong_password": {
                        "summary": "Неверный пароль",
                        "value": {
                            "detail": [
                                {
                                    "type": "value_error",
                                    "loc": ["body", "password"],
                                    "msg": "Неверный пароль",
                                    "input": "wrongpassword",
                                    "ctx": {
                                        "reason": "Invalid password"
                                    }
                                }
                            ]
                        }
                    }
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
                    "detail": [
                        {
                            "type": "forbidden",
                            "loc": ["body", "email"],
                            "msg": "Проверьте почту для подтверждения email",
                            "input": "unverified@email.com",
                            "ctx": {
                                "reason": "Email not verified"
                            }
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
        "description": "Ошибка валидации данных (FastAPI / Pydantic)",
        "content": {
            "application/json": {
                "examples": {
                    "missing_field": {
                        "summary": "Отсутствует обязательное поле",
                        "value": {
                            "detail": [
                                {
                                    "type": "missing",
                                    "loc": ["body", "password"],
                                    "msg": "Поле обязательно для заполнения",
                                    "input": {
                                        "email": "user@example.com"
                                    }
                                }
                            ]
                        }
                    },
                    "invalid_email_format": {
                        "summary": "Некорректный формат email",
                        "value": {
                            "detail": [
                                {
                                    "type": "value_error",
                                    "loc": ["body", "email"],
                                    "msg": "Некорректный формат email адреса: email должен содержать символ @",
                                    "input": "invalid-email",
                                    "ctx": {
                                        "reason": "Email должен содержать символ @"
                                    }
                                }
                            ]
                        }
                    }
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
                    "detail": [
                        {
                            "type": "server_error",
                            "loc": ["body"],
                            "msg": "Сервер временно недоступен. Попробуйте позже.",
                            "input": {},
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

# Объединенные responses для входа
USER_LOGIN_RESPONSES = {
    **USER_LOGIN_SUCCESS,
    **USER_LOGIN_BUSINESS_ERROR,
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
        "description": "Access токен успешно обновлен",
        "content": {
            "application/json": {
                "example": {
                    "message": "Токен успешно обновлен",
                    "data": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer"
                    }
                }
            }
        },
        "headers": {
            "Set-Cookie": {
                "description": "Новые refresh токен и CSRF токен устанавливаются в httpOnly cookies",
                "schema": {
                    "type": "string",
                    "example": "jwt=<new_refresh_token>; HttpOnly; Secure; SameSite=Strict; csrf_token=<new_csrf_token>; HttpOnly; Secure; SameSite=Strict"
                }
            }
        }
    }
}

REFRESH_TOKEN_AUTH_ERROR = {
    401: {
        "model": ErrorResponse,
        "description": "Невалидный или истекший refresh токен (куки автоматически удаляются)",
        "content": {
            "application/json": {
                "examples": {
                    "missing_cookie": {
                        "summary": "Refresh токен не найден в куках",
                        "value": {
                            "detail": [
                                {
                                    "type": "value_error",
                                    "loc": ["body", "token"],
                                    "msg": "Refresh токен не найден в куках",
                                    "input": None,
                                    "ctx": {
                                        "reason": "Invalid cookie"
                                    }
                                }
                            ]
                        }
                    },
                    "expired_token": {
                        "summary": "Refresh токен истек",
                        "value": {
                            "detail": [
                                {
                                    "type": "value_error",
                                    "loc": ["body", "token"],
                                    "msg": "Refresh токен истек",
                                    "input": "***",
                                    "ctx": {
                                        "reason": "Invalid token"
                                    }
                                }
                            ]
                        }
                    },
                    "invalid_token": {
                        "summary": "Невалидный refresh токен",
                        "value": {
                            "detail": [
                                {
                                    "type": "value_error",
                                    "loc": ["body", "token"],
                                    "msg": "Невалидный refresh токен",
                                    "input": "***",
                                    "ctx": {
                                        "reason": "Invalid token"
                                    }
                                }
                            ]
                        }
                    },
                    "wrong_token_type": {
                        "summary": "Неверный тип токена",
                        "value": {
                            "detail": [
                                {
                                    "type": "value_error",
                                    "loc": ["body", "token"],
                                    "msg": "Неверный тип токена",
                                    "input": "***",
                                    "ctx": {
                                        "reason": "Invalid token"
                                    }
                                }
                            ]
                        }
                    }
                }
            },
        },
    }
}

REFRESH_TOKEN_CSRF_ERROR = {
    403: {
        "model": ErrorResponse,
        "description": "CSRF токен отсутствует или невалиден",
        "content": {
            "application/json": {
                "examples": {
                    "missing_csrf_cookie": {
                        "summary": "CSRF токен не найден в cookie",
                        "value": {
                            "detail": [
                                {
                                    "type": "csrf_error",
                                    "loc": ["cookie"],
                                    "msg": "CSRF токен отсутствует в cookie",
                                    "input": None,
                                    "ctx": {
                                        "reason": "Missing CSRF cookie"
                                    }
                                }
                            ]
                        }
                    },
                    "missing_csrf_header": {
                        "summary": "CSRF токен не найден в заголовке",
                        "value": {
                            "detail": [
                                {
                                    "type": "csrf_error",
                                    "loc": ["header"],
                                    "msg": "CSRF токен отсутствует в заголовке X-CSRF-Token",
                                    "input": None,
                                    "ctx": {
                                        "reason": "Missing CSRF header"
                                    }
                                }
                            ]
                        }
                    },
                    "csrf_mismatch": {
                        "summary": "CSRF токены не совпадают",
                        "value": {
                            "detail": [
                                {
                                    "type": "csrf_error",
                                    "loc": ["token"],
                                    "msg": "CSRF токен из cookie не совпадает с токеном из заголовка",
                                    "input": "***",
                                    "ctx": {
                                        "reason": "CSRF token mismatch"
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

REFRESH_TOKEN_SERVER_ERROR = {
    500: {
        "model": ErrorResponse,
        "description": "Серверная ошибка",
        "content": {
            "application/json": {
                "example": {
                    "detail": [
                        {
                            "type": "server_error",
                            "loc": ["body"],
                            "msg": "Сервер временно недоступен. Попробуйте позже.",
                            "input": {},
                            "ctx": {
                                "reason": "Internal server error"
                            }
                        }
                    ]
                }
            },
        },
    }
}

# Объединенные responses для обновления токена
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
        "description": "Пользователь авторизован",
        "content": {
            "application/json": {
                "example": {
                    "message": "Пользователь авторизован",
                    "authorized": True
                }
            }
        }
    }
}

ACCESS_TOKEN_NOT_FOUND_ERROR = {
    404: {
        "model": ErrorResponse,
        "description": "Access токен не найден в заголовке Authorization",
        "content": {
            "application/json": {
                "example": {
                    "detail": [
                        {
                            "type": "not_found",
                            "loc": ["header", "Authorization"],
                            "msg": "Токен не найден в заголовке Authorization",
                            "input": None,
                            "ctx": {
                                "reason": "Missing Authorization header"
                            }
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
        "description": "Невалидный или истекший access токен",
        "content": {
            "application/json": {
                "examples": {
                    "invalid_format": {
                        "summary": "Неверный формат токена",
                        "value": {
                            "detail": [
                                {
                                    "type": "value_error",
                                    "loc": ["header", "Authorization"],
                                    "msg": "Неверный формат токена. Ожидается 'Bearer <token>'",
                                    "input": "Basic",
                                    "ctx": {
                                        "reason": "Invalid token format"
                                    }
                                }
                            ]
                        }
                    },
                    "empty_token": {
                        "summary": "Токен не найден после 'Bearer'",
                        "value": {
                            "detail": [
                                {
                                    "type": "value_error",
                                    "loc": ["header", "Authorization"],
                                    "msg": "Токен не найден после 'Bearer'",
                                    "input": "",
                                    "ctx": {
                                        "reason": "Empty token"
                                    }
                                }
                            ]
                        }
                    },
                    "expired_token": {
                        "summary": "Access токен истек",
                        "value": {
                            "detail": [
                                {
                                    "type": "value_error",
                                    "loc": ["header", "token"],
                                    "msg": "Access токен истек",
                                    "input": "***",
                                    "ctx": {
                                        "reason": "Invalid token"
                                    }
                                }
                            ]
                        }
                    },
                    "invalid_token": {
                        "summary": "Невалидный access токен",
                        "value": {
                            "detail": [
                                {
                                    "type": "value_error",
                                    "loc": ["header", "token"],
                                    "msg": "Невалидный access токен",
                                    "input": "***",
                                    "ctx": {
                                        "reason": "Invalid token"
                                    }
                                }
                            ]
                        }
                    },
                    "wrong_token_type": {
                        "summary": "Неверный тип токена",
                        "value": {
                            "detail": [
                                {
                                    "type": "value_error",
                                    "loc": ["header", "token"],
                                    "msg": "Неверный тип токена. Ожидается access токен",
                                    "input": "***",
                                    "ctx": {
                                        "reason": "Wrong token type"
                                    }
                                }
                            ]
                        }
                    },
                    "missing_user_id": {
                        "summary": "ID пользователя не найден в токене",
                        "value": {
                            "detail": [
                                {
                                    "type": "value_error",
                                    "loc": ["header", "token"],
                                    "msg": "ID пользователя не найден в токене",
                                    "input": "***",
                                    "ctx": {
                                        "reason": "Missing user ID"
                                    }
                                }
                            ]
                        }
                    }
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
                    "detail": [
                        {
                            "type": "server_error",
                            "loc": ["header"],
                            "msg": "Ошибка при проверке токена",
                            "input": "***",
                            "ctx": {
                                "reason": "Token verification error"
                            }
                        }
                    ]
                }
            },
        },
    }
}

# Объединенные responses для проверки access токена
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
        "description": "Данные текущего пользователя успешно получены",
        "content": {
            "application/json": {
                "example": {
                    "id": 123,
                    "username": "testuser",
                    "email": "test@example.com",
                    "avatar_url": "https://example.com/avatar.jpg",
                    "is_admin": False,
                    "created_at": "2024-01-15T10:30:00Z",
                    "updated_at": "2024-01-15T10:30:00Z"
                }
            }
        }
    }
}

USER_BY_ID_NOT_FOUND_ERROR = {
    404: {
        "model": ErrorResponse,
        "description": "Пользователь не найден в базе данных",
        "content": {
            "application/json": {
                "example": {
                    "detail": [
                        {
                            "type": "not_found",
                            "loc": ["body", "id"],
                            "msg": "Пользователь с ID 123 не найден",
                            "input": None,
                            "ctx": {
                                "reason": "User not found"
                            }
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
                    "detail": [
                        {
                            "type": "server_error",
                            "loc": ["body"],
                            "msg": "Сервер временно недоступен. Попробуйте позже.",
                            "input": {},
                            "ctx": {
                                "reason": "Internal server error"
                            }
                        }
                    ]
                }
            },
        },
    }
}

# Объединенные responses для получения пользователя по ID
USER_BY_ID_RESPONSES = {
    **USER_BY_ID_SUCCESS,
    **ACCESS_TOKEN_NOT_FOUND_ERROR,
    **ACCESS_TOKEN_AUTH_ERROR,
    **USER_BY_ID_NOT_FOUND_ERROR,
    **USER_BY_ID_SERVER_ERROR,
}

# =============================================================================
# USER DELETE RESPONSES
# =============================================================================

USER_DELETE_SUCCESS = {
    200: {
        "description": "Пользователь успешно удален",
        "content": {
            "application/json": {
                "example": {
                    "message": "Пользователь успешно удален",
                    "data": {
                        "user_id": 123
                    }
                }
            }
        }
    }
}

USER_DELETE_NOT_FOUND_ERROR = {
    404: {
        "model": ErrorResponse,
        "description": "Пользователь не найден в базе данных",
        "content": {
            "application/json": {
                "example": {
                    "detail": [
                        {
                            "type": "not_found",
                            "loc": ["body", "id"],
                            "msg": "Пользователь с ID 123 не найден",
                            "input": 123,
                            "ctx": {
                                "reason": "User not found in database"
                            }
                        }
                    ]
                }
            },
        },
    }
}

USER_DELETE_SERVER_ERROR = {
    500: {
        "model": ErrorResponse,
        "description": "Серверная ошибка",
        "content": {
            "application/json": {
                "example": {
                    "detail": [
                        {
                            "type": "server_error",
                            "loc": ["body"],
                            "msg": "Сервер временно недоступен. Попробуйте позже.",
                            "input": {},
                            "ctx": {
                                "reason": "Internal server error"
                            }
                        }
                    ]
                }
            },
        },
    }
}

# Объединенные responses для удаления пользователя
USER_DELETE_RESPONSES = {
    **USER_DELETE_SUCCESS,
    **ACCESS_TOKEN_NOT_FOUND_ERROR,
    **ACCESS_TOKEN_AUTH_ERROR,
    **USER_DELETE_NOT_FOUND_ERROR,
    **USER_DELETE_SERVER_ERROR,
}

# =============================================================================
# USER UPDATE PROFILE RESPONSES
# =============================================================================

USER_UPDATE_PROFILE_SUCCESS = {
    200: {
        "description": "Профиль пользователя успешно обновлен",
        "content": {
            "application/json": {
                "example": {
                    "message": "Профиль успешно обновлен",
                    "data": {
                        "id": 123,
                        "username": "new_username",
                        "email": "user@example.com",
                        "avatar_url": "https://example.com/avatar.jpg",
                        "is_admin": False
                    }
                }
            }
        }
    }
}

USER_UPDATE_PROFILE_NOT_FOUND_ERROR = {
    404: {
        "model": ErrorResponse,
        "description": "Пользователь не найден",
        "content": {
            "application/json": {
                "example": {
                    "detail": [
                        {
                            "type": "not_found",
                            "loc": ["body", "id"],
                            "msg": "Пользователь с ID 123 не найден",
                            "input": 123,
                            "ctx": {
                                "reason": "User not found"
                            }
                        }
                    ]
                }
            },
        },
    }
}

USER_UPDATE_PROFILE_VALIDATION_ERROR = {
    422: {
        "model": ErrorResponse,
        "description": "Ошибка валидации данных",
        "content": {
            "application/json": {
                "examples": {
                    "username_too_short": {
                        "summary": "Имя пользователя слишком короткое",
                        "value": {
                            "detail": [
                                {
                                    "type": "string_too_short",
                                    "loc": ["body", "username"],
                                    "msg": "Строка должна содержать минимум 3 символов",
                                    "input": "ab",
                                    "ctx": {
                                        "min_length": 3
                                    }
                                }
                            ]
                        }
                    },
                    "empty_request": {
                        "summary": "Не указаны поля для обновления",
                        "value": {
                            "detail": [
                                {
                                    "type": "value_error",
                                    "loc": ["body"],
                                    "msg": "Необходимо указать хотя бы одно поле для обновления",
                                    "input": {},
                                    "ctx": {
                                        "reason": "No fields to update"
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

USER_UPDATE_PROFILE_SERVER_ERROR = {
    500: {
        "model": ErrorResponse,
        "description": "Серверная ошибка",
        "content": {
            "application/json": {
                "example": {
                    "detail": [
                        {
                            "type": "server_error",
                            "loc": ["body"],
                            "msg": "Сервер временно недоступен. Попробуйте позже.",
                            "input": {},
                            "ctx": {
                                "reason": "Internal server error"
                            }
                        }
                    ]
                }
            },
        },
    }
}

# Объединенные responses для обновления профиля
USER_UPDATE_PROFILE_RESPONSES = {
    **USER_UPDATE_PROFILE_SUCCESS,
    **ACCESS_TOKEN_NOT_FOUND_ERROR,
    **ACCESS_TOKEN_AUTH_ERROR,
    **USER_UPDATE_PROFILE_NOT_FOUND_ERROR,
    **USER_UPDATE_PROFILE_VALIDATION_ERROR,
    **USER_UPDATE_PROFILE_SERVER_ERROR,
}