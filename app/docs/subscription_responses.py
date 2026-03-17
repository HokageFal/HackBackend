"""
Документация ответов для эндпоинтов подписок.
"""

from app.schemas.api_response import ErrorResponse, SuccessResponse

# =============================================================================
# 1. ПОЛУЧЕНИЕ ТАРИФНЫХ ПЛАНОВ (GET /subscriptions/plans)
# =============================================================================

SUBSCRIPTION_PLANS_SUCCESS = {
    200: {
        "model": SuccessResponse,
        "description": "Список тарифных планов успешно получен",
        "content": {
            "application/json": {
                "example": {
                    "status": "success",
                    "message": "Тарифные планы получены успешно",
                    "data": {
                        "plans": {
                            "monthly": [
                                {
                                    "id": 1,
                                    "name": "Pro Monthly",
                                    "description": "Ежемесячный план для профи",
                                    "price": 29.99,
                                    "tokens": 1000,
                                    "features": ["Feature 1", "Feature 2"],
                                    "duration_days": 30
                                }
                            ],
                            "yearly": [
                                {
                                    "id": 2,
                                    "name": "Pro Yearly",
                                    "description": "Выгодный годовой план",
                                    "price": 299.99,
                                    "tokens": 15000,
                                    "features": ["All features", "Priority support"],
                                    "duration_days": 365
                                }
                            ]
                        }
                    },
                    "errors": None
                }
            }
        }
    }
}

SUBSCRIPTION_PLANS_ERROR = {
    404: {
        "model": ErrorResponse,
        "description": "Тарифные планы не найдены в базе данных",
        "content": {
            "application/json": {
                "example": {
                    "status": "error",
                    "message": "Тарифные планы не найдены",
                    "data": None,
                    "errors": [
                        {
                            "type": "not_found_error",
                            "field": "subscription_plans",
                            "message": "Тарифные планы не найдены",
                            "input": "",
                            "ctx": {"reason": "No subscription plans found"}
                        }
                    ]
                }
            }
        }
    }
}

# =============================================================================
# 2. ТЕКУЩАЯ ПОДПИСКА (GET /subscriptions/current)
# =============================================================================

CURRENT_SUBSCRIPTION_SUCCESS = {
    200: {
        "model": SuccessResponse,
        "description": "Активная подписка пользователя",
        "content": {
            "application/json": {
                "example": {
                    "status": "success",
                    "message": "Подписка пользователя получена успешно",
                    "data": {
                        "subscription": {
                            "id": 45,
                            "plan_id": 1,
                            "user_id": 10,
                            "started_at": "2023-10-01T12:00:00",
                            "expires_at": "2023-11-01T12:00:00",
                            "is_active": True
                        }
                    },
                    "errors": None
                }
            }
        }
    }
}

CURRENT_SUBSCRIPTION_ERRORS = {
    404: {
        "model": ErrorResponse,
        "description": "Пользователь или подписка не найдены",
        "content": {
            "application/json": {
                "examples": {
                    "user_not_found": {
                        "summary": "Пользователь не найден",
                        "value": {
                            "status": "error",
                            "message": "Пользователь с ID 10 не найден",
                            "data": None,
                            "errors": [
                                {
                                    "type": "not_found_error",
                                    "field": "id",
                                    "message": "Пользователь с ID 10 не найден",
                                    "input": 10,
                                    "ctx": {"reason": "User not found in database"}
                                }
                            ]
                        }
                    },
                    "subscription_not_found": {
                        "summary": "Подписка не найдена",
                        "value": {
                            "status": "error",
                            "message": "Подписка пользователя не найдена",
                            "data": None,
                            "errors": [
                                {
                                    "type": "not_found_error",
                                    "field": "subscription",
                                    "message": "Подписка пользователя не найдена",
                                    "input": 10,
                                    "ctx": {"reason": "Subscription not found"}
                                }
                            ]
                        }
                    }
                }
            }
        }
    }
}

# =============================================================================
# 3. ДОБАВЛЕНИЕ ПОДПИСКИ (POST /subscriptions/add)
# =============================================================================

ADD_SUBSCRIPTION_SUCCESS = {
    200: {
        "model": SuccessResponse,
        "description": "Подписка успешно оформлена",
        "content": {
            "application/json": {
                "example": {
                    "status": "success",
                    "message": "Подписка успешно добавлена пользователю 10",
                    "data": None,
                    "errors": None
                }
            }
        }
    }
}

# =============================================================================
# 4. ИСТОРИЯ ПОДПИСОК (GET /subscriptions/history)
# =============================================================================

SUBSCRIPTION_HISTORY_SUCCESS = {
    200: {
        "model": SuccessResponse,
        "description": "История всех подписок пользователя",
        "content": {
            "application/json": {
                "example": {
                    "status": "success",
                    "message": "История подписок получена успешно",
                    "data": {
                        "subscriptions": [
                            {
                                "subscription_id": 45,
                                "plan_name": "Pro Monthly",
                                "plan_description": "Description...",
                                "tokens": 1000,
                                "duration_days": 30,
                                "started_at": "2023-10-01T12:00:00",
                                "expires_at": "2023-11-01T12:00:00",
                                "is_active": True
                            },
                            {
                                "subscription_id": 12,
                                "plan_name": "Free",
                                "plan_description": "Initial plan",
                                "tokens": 100,
                                "duration_days": 30,
                                "started_at": "2023-09-01T10:00:00",
                                "expires_at": "2023-10-01T10:00:00",
                                "is_active": False
                            }
                        ]
                    },
                    "errors": None
                }
            }
        }
    }
}

# =============================================================================
# ОБЩИЕ ОШИБКИ (500)
# =============================================================================

COMMON_SERVER_ERROR = {
    500: {
        "model": ErrorResponse,
        "description": "Внутренняя ошибка сервера",
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
            }
        }
    }
}

# Группировка для роутера
SUBSCRIPTION_PLANS_RESPONSES = {**SUBSCRIPTION_PLANS_SUCCESS, **SUBSCRIPTION_PLANS_ERROR, **COMMON_SERVER_ERROR}
CURRENT_SUBSCRIPTION_RESPONSES = {**CURRENT_SUBSCRIPTION_SUCCESS, **CURRENT_SUBSCRIPTION_ERRORS, **COMMON_SERVER_ERROR}
ADD_SUBSCRIPTION_RESPONSES = {**ADD_SUBSCRIPTION_SUCCESS, **CURRENT_SUBSCRIPTION_ERRORS, **COMMON_SERVER_ERROR}
HISTORY_RESPONSES = {**SUBSCRIPTION_HISTORY_SUCCESS, **CURRENT_SUBSCRIPTION_ERRORS, **COMMON_SERVER_ERROR}