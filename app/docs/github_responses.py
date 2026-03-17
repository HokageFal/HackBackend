"""
Документация ответов для GitHub OAuth
"""

GITHUB_AUTH_RESPONSES = {
    200: {
        "description": "Успешная авторизация через GitHub",
        "content": {
            "application/json": {
                "example": {
                    "status": "success",
                    "message": "Вход через GitHub выполнен успешно",
                    "data": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer",
                        "user": {
                            "id": 1,
                            "username": "github_username",
                            "email": "user@example.com",
                            "avatar_url": "https://avatars.githubusercontent.com/u/123456",
                            "is_admin": False,
                            "created_at": "2024-01-15T10:30:00",
                            "token_balance": 0
                        }
                    }
                }
            }
        }
    },
    400: {
        "description": "Ошибка бизнес-логики (неверный или истекший код)",
        "content": {
            "application/json": {
                "examples": {
                    "expired_code": {
                        "summary": "Истекший или использованный код",
                        "value": {
                            "status": "error",
                            "message": "Ошибка бизнес-логики",
                            "errors": [
                                {
                                    "type": "business_error",
                                    "field": "code",
                                    "message": "Неверный или истекший код авторизации GitHub",
                                    "ctx": {
                                        "reason": "The code passed is incorrect or expired."
                                    }
                                }
                            ]
                        }
                    },
                    "no_token": {
                        "summary": "Не удалось получить токен",
                        "value": {
                            "status": "error",
                            "message": "Ошибка бизнес-логики",
                            "errors": [
                                {
                                    "type": "business_error",
                                    "field": "code",
                                    "message": "Не удалось получить токен от GitHub",
                                    "ctx": {
                                        "reason": "No access_token in response"
                                    }
                                }
                            ]
                        }
                    },
                    "user_fetch_failed": {
                        "summary": "Не удалось получить данные пользователя",
                        "value": {
                            "status": "error",
                            "message": "Ошибка бизнес-логики",
                            "errors": [
                                {
                                    "type": "business_error",
                                    "field": "code",
                                    "message": "Не удалось получить данные пользователя от GitHub",
                                    "ctx": {
                                        "reason": "GitHub API returned 401"
                                    }
                                }
                            ]
                        }
                    }
                }
            }
        }
    },
    422: {
        "description": "Ошибка валидации запроса",
        "content": {
            "application/json": {
                "example": {
                    "detail": [
                        {
                            "type": "missing",
                            "loc": ["body", "code"],
                            "msg": "Field required",
                            "input": {}
                        }
                    ]
                }
            }
        }
    },
    500: {
        "description": "Внутренняя ошибка сервера",
        "content": {
            "application/json": {
                "example": {
                    "status": "error",
                    "message": "Внутренняя ошибка сервера",
                    "errors": [
                        {
                            "type": "server_error",
                            "message": "Произошла непредвиденная ошибка. Попробуйте позже"
                        }
                    ]
                }
            }
        }
    }
}
