"""
Документация ответов для Password Reset эндпоинтов.

Все ответы следуют унифицированному формату API:
{
    "status": "success" | "error",
    "message": "Описание результата операции",
    "data": { /* полезная нагрузка */ },
    "errors": [{ /* детали ошибок */ }]
}
"""

from app.schemas.api_response import ErrorResponse, SuccessResponse

# =============================================================================
# PASSWORD RESET REQUEST RESPONSES
# =============================================================================

PASSWORD_RESET_REQUEST_SUCCESS = {
    200: {
        "model": SuccessResponse,
        "description": "Запрос на сброс пароля принят",
        "content": {
            "application/json": {
                "example": {
                    "status": "success",
                    "message": "Если пользователь существует, код отправлен на email",
                    "data": {
                        "email": "user@example.com"
                    },
                    "errors": None
                }
            }
        }
    }
}

PASSWORD_RESET_REQUEST_VALIDATION_ERROR = {
    422: {
        "model": ErrorResponse,
        "description": "Ошибка валидации email",
        "content": {
            "application/json": {
                "examples": {
                    "invalid_email_format": {
                        "summary": "Некорректный формат email",
                        "value": {
                            "detail": [
                                {
                                    "type": "value_error",
                                    "loc": ["body", "email"],
                                    "msg": "Некорректный формат email",
                                    "input": "invalid-email",
                                    "ctx": {}
                                }
                            ]
                        }
                    },
                    "missing_email": {
                        "summary": "Отсутствует email",
                        "value": {
                            "detail": [
                                {
                                    "type": "missing",
                                    "loc": ["body", "email"],
                                    "msg": "Поле обязательно для заполнения",
                                    "input": None,
                                    "ctx": {}
                                }
                            ]
                        }
                    }
                }
            }
        }
    }
}

PASSWORD_RESET_REQUEST_SERVER_ERROR = {
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

PASSWORD_RESET_REQUEST_RESPONSES = {
    **PASSWORD_RESET_REQUEST_SUCCESS,
    **PASSWORD_RESET_REQUEST_VALIDATION_ERROR,
    **PASSWORD_RESET_REQUEST_SERVER_ERROR,
}

# =============================================================================
# PASSWORD RESET VERIFY RESPONSES
# =============================================================================

PASSWORD_RESET_VERIFY_SUCCESS = {
    200: {
        "model": SuccessResponse,
        "description": "Пароль успешно изменен",
        "content": {
            "application/json": {
                "example": {
                    "status": "success",
                    "message": "Пароль успешно изменен",
                    "data": {
                        "email": "user@example.com"
                    },
                    "errors": None
                }
            }
        }
    }
}

PASSWORD_RESET_VERIFY_INVALID_CODE_ERROR = {
    400: {
        "model": ErrorResponse,
        "description": "Неверный код, превышены попытки, или невалидная операция",
        "content": {
            "application/json": {
                "examples": {
                    "invalid_code": {
                        "summary": "Неверный код",
                        "value": {
                            "status": "error",
                            "message": "Ошибка бизнес-логики",
                            "data": None,
                            "errors": [
                                {
                                    "type": "business_error",
                                    "field": "code",
                                    "message": "Неверный код",
                                    "input": "123456",
                                    "ctx": {
                                        "reason": "Invalid verification code"
                                    }
                                }
                            ]
                        }
                    },
                    "code_expired": {
                        "summary": "Код истек или не найден",
                        "value": {
                            "status": "error",
                            "message": "Ошибка бизнес-логики",
                            "data": None,
                            "errors": [
                                {
                                    "type": "business_error",
                                    "field": "code",
                                    "message": "Код не найден или истек",
                                    "input": "123456",
                                    "ctx": {
                                        "reason": "Code not found or expired"
                                    }
                                }
                            ]
                        }
                    },
                    "max_attempts": {
                        "summary": "Превышены попытки",
                        "value": {
                            "status": "error",
                            "message": "Ошибка бизнес-логики",
                            "data": None,
                            "errors": [
                                {
                                    "type": "business_error",
                                    "field": "code",
                                    "message": "Превышено максимальное количество попыток",
                                    "input": "123456",
                                    "ctx": {
                                        "reason": "Invalid verification code"
                                    }
                                }
                            ]
                        }
                    },
                    "user_not_found": {
                        "summary": "Пользователь не найден",
                        "value": {
                            "status": "error",
                            "message": "Ошибка бизнес-логики",
                            "data": None,
                            "errors": [
                                {
                                    "type": "business_error",
                                    "field": "email",
                                    "message": "Пользователь с email user@example.com не найден",
                                    "input": "user@example.com",
                                    "ctx": {
                                        "reason": "User not found"
                                    }
                                }
                            ]
                        }
                    },
                    "oauth_user": {
                        "summary": "OAuth пользователь не может сбросить пароль",
                        "value": {
                            "status": "error",
                            "message": "Ошибка бизнес-логики",
                            "data": None,
                            "errors": [
                                {
                                    "type": "business_error",
                                    "field": "auth_provider",
                                    "message": "Невозможно сбросить пароль для пользователя с авторизацией через google",
                                    "input": "user@example.com",
                                    "ctx": {
                                        "reason": "Invalid operation for OAuth user"
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

PASSWORD_RESET_VERIFY_VALIDATION_ERROR = {
    422: {
        "model": ErrorResponse,
        "description": "Ошибка валидации данных",
        "content": {
            "application/json": {
                "examples": {
                    "weak_password": {
                        "summary": "Слабый пароль - нет заглавной буквы",
                        "value": {
                            "detail": [
                                {
                                    "type": "value_error",
                                    "loc": ["body", "new_password"],
                                    "msg": "Пароль должен содержать хотя бы одну заглавную букву",
                                    "input": "password123",
                                    "ctx": {}
                                }
                            ]
                        }
                    },
                    "short_password": {
                        "summary": "Короткий пароль",
                        "value": {
                            "detail": [
                                {
                                    "type": "string_too_short",
                                    "loc": ["body", "new_password"],
                                    "msg": "Строка должна содержать минимум 8 символов",
                                    "input": "Pass1",
                                    "ctx": {
                                        "min_length": "8"
                                    }
                                }
                            ]
                        }
                    },
                    "invalid_code_format": {
                        "summary": "Неверный формат кода",
                        "value": {
                            "detail": [
                                {
                                    "type": "value_error",
                                    "loc": ["body", "code"],
                                    "msg": "Код должен содержать только цифры",
                                    "input": "abc123",
                                    "ctx": {}
                                }
                            ]
                        }
                    },
                    "invalid_code_length": {
                        "summary": "Неверная длина кода",
                        "value": {
                            "detail": [
                                {
                                    "type": "string_too_short",
                                    "loc": ["body", "code"],
                                    "msg": "Строка должна содержать минимум 6 символов",
                                    "input": "12345",
                                    "ctx": {
                                        "min_length": "6"
                                    }
                                }
                            ]
                        }
                    },
                    "missing_fields": {
                        "summary": "Отсутствуют обязательные поля",
                        "value": {
                            "detail": [
                                {
                                    "type": "missing",
                                    "loc": ["body", "new_password"],
                                    "msg": "Поле обязательно для заполнения",
                                    "input": {
                                        "email": "user@example.com",
                                        "code": "123456"
                                    },
                                    "ctx": {}
                                }
                            ]
                        }
                    }
                }
            }
        }
    }
}

PASSWORD_RESET_VERIFY_SERVER_ERROR = {
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

PASSWORD_RESET_VERIFY_RESPONSES = {
    **PASSWORD_RESET_VERIFY_SUCCESS,
    **PASSWORD_RESET_VERIFY_INVALID_CODE_ERROR,
    **PASSWORD_RESET_VERIFY_VALIDATION_ERROR,
    **PASSWORD_RESET_VERIFY_SERVER_ERROR,
}
