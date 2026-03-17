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
        "model": OtpResponse,
        "description": "OTP код успешно отправлен на email",
        "content": {
            "application/json": {
                "example": {
                    "status": "success",
                    "message": "Код подтверждения отправлен на email",
                    "data": {
                        "email": "user@example.com",
                        "expires_in_seconds": 600
                    },
                    "errors": None
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
                    "status": "error",
                    "message": "Превышен лимит запросов",
                    "data": None,
                    "errors": [
                        {
                            "type": "rate_limit",
                            "field": "email",
                            "message": "Слишком частые запросы. Попробуйте через 1 минуту",
                            "input": "user@example.com",
                            "ctx": {
                                "reason": "Rate limit exceeded",
                                "retry_after": 60
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
                            "status": "error",
                            "message": "Ошибка валидации данных",
                            "data": None,
                            "errors": [
                                {
                                    "type": "validation_error",
                                    "field": "email",
                                    "message": "Некорректный формат email адреса",
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
                            "status": "error",
                            "message": "Ошибка валидации данных",
                            "data": None,
                            "errors": [
                                {
                                    "type": "missing",
                                    "field": "email",
                                    "message": "Поле обязательно для заполнения",
                                    "input": None,
                                    "ctx": {
                                        "reason": "Missing required field"
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

OTP_SEND_SERVER_ERROR = {
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
        "model": OtpResponse,
        "description": "OTP код успешно проверен",
        "content": {
            "application/json": {
                "example": {
                    "status": "success",
                    "message": "Email успешно подтвержден",
                    "data": {
                        "email": "user@example.com",
                        "verified": True
                    },
                    "errors": None
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
                                        "reason": "Max verification attempts exceeded"
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
                    "status": "error",
                    "message": "Ресурс не найден",
                    "data": None,
                    "errors": [
                        {
                            "type": "not_found",
                            "field": "code",
                            "message": "Код не найден или истек",
                            "input": "123456",
                            "ctx": {
                                "reason": "Verification code not found or expired"
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
                            "status": "error",
                            "message": "Ошибка валидации данных",
                            "data": None,
                            "errors": [
                                {
                                    "type": "validation_error",
                                    "field": "code",
                                    "message": "Код должен содержать ровно 6 цифр",
                                    "input": "12345",
                                    "ctx": {
                                        "reason": "Invalid code length",
                                        "expected_length": 6
                                    }
                                }
                            ]
                        }
                    },
                    "invalid_email": {
                        "summary": "Неверный email",
                        "value": {
                            "status": "error",
                            "message": "Ошибка валидации данных",
                            "data": None,
                            "errors": [
                                {
                                    "type": "validation_error",
                                    "field": "email",
                                    "message": "Некорректный формат email адреса",
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
                            "status": "error",
                            "message": "Ошибка валидации данных",
                            "data": None,
                            "errors": [
                                {
                                    "type": "missing",
                                    "field": "code",
                                    "message": "Поле обязательно для заполнения",
                                    "input": {
                                        "email": "user@example.com"
                                    },
                                    "ctx": {
                                        "reason": "Missing required field"
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

OTP_VERIFY_SERVER_ERROR = {
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

# Объединенные responses для проверки OTP
OTP_VERIFY_RESPONSES = {
    **OTP_VERIFY_SUCCESS,
    **OTP_VERIFY_INVALID_CODE_ERROR,
    **OTP_VERIFY_NOT_FOUND_ERROR,
    **OTP_VERIFY_VALIDATION_ERROR,
    **OTP_VERIFY_SERVER_ERROR,
}