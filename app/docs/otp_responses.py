"""
Документация ответов для OTP эндпоинтов.

Все ответы следуют унифицированному формату API:
{
    "status": "success" | "error",
    "message": "Описание результата операции",
    "data": { /* полезная нагрузка */ },
    "errors": [{ /* детали ошибок */ }]
}
"""

from app.schemas.api_response import ErrorResponse, OtpResponse

# =============================================================================
# OTP SEND RESPONSES
# =============================================================================

OTP_SEND_SUCCESS = {
    200: {
        "description": "OTP код успешно отправлен на email",
        "content": {
            "application/json": {
                "example": {
                    "message": "Код подтверждения отправлен на email",
                    "email": "user@example.com",
                    "expires_in_seconds": 600
                }
            }
        }
    }
}

OTP_SEND_RATE_LIMIT_ERROR = {
    429: {
        "model": ErrorResponse,
        "description": "Превышен лимит запросов",
        "content": {
            "application/json": {
                "example": {
                    "detail": [
                        {
                            "type": "value_error",
                            "loc": ["body", "email"],
                            "msg": "Слишком частые запросы. Попробуйте через 1 минуту",
                            "input": "user@example.com",
                            "ctx": {
                                "reason": "Rate limit exceeded"
                            }
                        }
                    ]
                }
            }
        }
    }
}

OTP_SEND_VALIDATION_ERROR = {
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
                                    "msg": "Некорректный формат email адреса",
                                    "input": "invalid-email",
                                    "ctx": {
                                        "reason": "Invalid email format"
                                    }
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
                                    "input": {},
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

OTP_SEND_SERVER_ERROR = {
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

# Объединенные responses для отправки OTP
OTP_SEND_RESPONSES = {
    **OTP_SEND_SUCCESS,
    **OTP_SEND_RATE_LIMIT_ERROR,
    **OTP_SEND_VALIDATION_ERROR,
    **OTP_SEND_SERVER_ERROR,
}

# =============================================================================
# OTP VERIFY RESPONSES
# =============================================================================

OTP_VERIFY_SUCCESS = {
    200: {
        "description": "OTP код успешно проверен",
        "content": {
            "application/json": {
                "example": {
                    "message": "Email успешно подтвержден",
                    "email": "user@example.com",
                    "verified": True
                }
            }
        }
    }
}

OTP_VERIFY_INVALID_CODE_ERROR = {
    400: {
        "model": ErrorResponse,
        "description": "Неверный код или превышены попытки",
        "content": {
            "application/json": {
                "examples": {
                    "invalid_code": {
                        "summary": "Неверный код",
                        "value": {
                            "detail": [
                                {
                                    "type": "value_error",
                                    "loc": ["body", "code"],
                                    "msg": "Неверный код",
                                    "input": "123456",
                                    "ctx": {
                                        "reason": "Invalid code"
                                    }
                                }
                            ]
                        }
                    },
                    "max_attempts": {
                        "summary": "Превышены попытки",
                        "value": {
                            "detail": [
                                {
                                    "type": "value_error",
                                    "loc": ["body", "code"],
                                    "msg": "Превышено максимальное количество попыток",
                                    "input": "123456",
                                    "ctx": {
                                        "reason": "Max attempts exceeded"
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

OTP_VERIFY_NOT_FOUND_ERROR = {
    404: {
        "model": ErrorResponse,
        "description": "Код не найден или истек",
        "content": {
            "application/json": {
                "example": {
                    "detail": [
                        {
                            "type": "not_found",
                            "loc": ["body", "code"],
                            "msg": "Код не найден или истек",
                            "input": "123456",
                            "ctx": {
                                "reason": "Code not found or expired"
                            }
                        }
                    ]
                }
            }
        }
    }
}

OTP_VERIFY_VALIDATION_ERROR = {
    422: {
        "model": ErrorResponse,
        "description": "Ошибка валидации данных",
        "content": {
            "application/json": {
                "examples": {
                    "invalid_code_length": {
                        "summary": "Неверная длина кода",
                        "value": {
                            "detail": [
                                {
                                    "type": "value_error",
                                    "loc": ["body", "code"],
                                    "msg": "Код должен содержать ровно 6 цифр",
                                    "input": "12345",
                                    "ctx": {
                                        "reason": "Invalid code length"
                                    }
                                }
                            ]
                        }
                    },
                    "invalid_email": {
                        "summary": "Неверный email",
                        "value": {
                            "detail": [
                                {
                                    "type": "value_error",
                                    "loc": ["body", "email"],
                                    "msg": "Некорректный формат email адреса",
                                    "input": "invalid-email",
                                    "ctx": {
                                        "reason": "Invalid email format"
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
                                    "loc": ["body", "code"],
                                    "msg": "Поле обязательно для заполнения",
                                    "input": {
                                        "email": "user@example.com"
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

OTP_VERIFY_SERVER_ERROR = {
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

# Объединенные responses для проверки OTP
OTP_VERIFY_RESPONSES = {
    **OTP_VERIFY_SUCCESS,
    **OTP_VERIFY_INVALID_CODE_ERROR,
    **OTP_VERIFY_NOT_FOUND_ERROR,
    **OTP_VERIFY_VALIDATION_ERROR,
    **OTP_VERIFY_SERVER_ERROR,
}
