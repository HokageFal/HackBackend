"""
Утилиты для создания унифицированных API ответов.

Этот модуль предоставляет функции для создания стандартизированных ответов API
в соответствии с единым форматом проекта.
"""

from fastapi import HTTPException
from typing import Any, Dict, List, Optional, Union
from app.schemas.api_response import (
    ApiResponse, 
    SuccessResponse, 
    ErrorResponse, 
    ApiError,
    AuthSuccessResponse,
    UserDataResponse,
    OtpResponse
)


def create_success_response(
    message: str,
    data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Создает успешный ответ API.
    
    Args:
        message: Описание результата операции
        data: Полезная нагрузка ответа
        
    Returns:
        Словарь с успешным ответом
    """
    response = SuccessResponse(
        message=message,
        data=data
    )
    return response.model_dump(exclude_none=True)


def create_auth_success_response(
    message: str,
    access_token: str,
    user_data: Optional[Dict[str, Any]] = None,
    token_type: str = "bearer"
) -> Dict[str, Any]:
    """
    Создает успешный ответ аутентификации.
    
    Args:
        message: Описание результата операции
        access_token: JWT access токен
        user_data: Данные пользователя
        token_type: Тип токена
        
    Returns:
        Словарь с успешным ответом аутентификации
        
    Note:
        Refresh и CSRF токены передаются только в httpOnly cookies, не в JSON
    """
    data = {
        "access_token": access_token,
        "token_type": token_type
    }
    
    if user_data:
        data["user"] = user_data
    
    response = AuthSuccessResponse(
        message=message,
        data=data
    )
    return response.model_dump(exclude_none=True)


def create_user_data_response(
    message: str,
    user_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Создает ответ с данными пользователя.
    
    Args:
        message: Описание результата операции
        user_data: Данные пользователя
        
    Returns:
        Словарь с данными пользователя
    """
    response = UserDataResponse(
        message=message,
        data=user_data
    )
    return response.model_dump(exclude_none=True)


def create_otp_response(
    message: str,
    email: str,
    expires_in_seconds: Optional[int] = None,
    verified: Optional[bool] = None
) -> Dict[str, Any]:
    data = {"email": email}
    
    if expires_in_seconds is not None:
        data["expires_in_seconds"] = expires_in_seconds
    
    if verified is not None:
        data["verified"] = verified
    
    response = OtpResponse(
        message=message,
        data=data
    )
    return response.model_dump(exclude_none=True)


def create_api_error(
    error_type: str,
    message: str,
    field: Optional[str] = None,
    input_data: Optional[Any] = None,
    ctx: Optional[Dict[str, Any]] = None
) -> ApiError:
    return ApiError(
        type=error_type,
        field=field,
        message=message,
        input=input_data,
        ctx=ctx or {}
    )


def create_error_response(
    message: str,
    errors: List[ApiError]
) -> Dict[str, Any]:
    """
    Создает ответ с ошибками API.
    
    Args:
        message: Общее описание ошибки
        errors: Список ошибок
        
    Returns:
        Словарь с ответом об ошибке
    """
    response = ErrorResponse(
        message=message,
        errors=errors
    )
    return response.model_dump(exclude_none=True)


def create_http_exception(
    status_code: int,
    message: str,
    errors: List[ApiError]
) -> HTTPException:
    """
    Создает HTTPException с унифицированным форматом ошибки.
    
    Args:
        status_code: HTTP код ошибки
        message: Общее описание ошибки
        errors: Список ошибок
        
    Returns:
        HTTPException с структурированной ошибкой
    """
    error_response = create_error_response(message, errors)
    return HTTPException(status_code=status_code, detail=error_response)


# Специализированные функции для создания типичных ошибок

def create_validation_error(
    field: str,
    message: str,
    input_data: Optional[Any] = None,
    reason: Optional[str] = None
) -> HTTPException:
    """
    Создает ошибку валидации (422 Unprocessable Entity).
    
    Args:
        field: Поле, которое не прошло валидацию
        message: Сообщение об ошибке
        input_data: Значение поля
        reason: Причина ошибки
        
    Returns:
        HTTPException с кодом 422
    """
    error = create_api_error(
        error_type="validation_error",
        message=message,
        field=field,
        input_data=input_data,
        ctx={"reason": reason or f"Validation failed for {field}"}
    )
    
    return create_http_exception(
        status_code=422,
        message="Ошибка валидации данных",
        errors=[error]
    )


def create_conflict_error(
    field: str,
    message: str,
    input_data: Optional[Any] = None,
    reason: Optional[str] = None
) -> HTTPException:
    """
    Создает ошибку конфликта (409 Conflict).
    
    Args:
        field: Поле, которое вызвало конфликт
        message: Сообщение об ошибке
        input_data: Значение поля
        reason: Причина конфликта
        
    Returns:
        HTTPException с кодом 409
    """
    error = create_api_error(
        error_type="conflict",
        message=message,
        field=field,
        input_data=input_data,
        ctx={"reason": reason or f"Conflict for {field}"}
    )
    
    return create_http_exception(
        status_code=409,
        message="Конфликт данных",
        errors=[error]
    )


def create_auth_error(
    field: str,
    message: str,
    input_data: Optional[Any] = None,
    reason: Optional[str] = None
) -> HTTPException:
    """
    Создает ошибку аутентификации (401 Unauthorized).
    
    Args:
        field: Поле, связанное с ошибкой аутентификации
        message: Сообщение об ошибке
        input_data: Значение поля
        reason: Причина ошибки
        
    Returns:
        HTTPException с кодом 401
    """
    error = create_api_error(
        error_type="unauthorized",
        message=message,
        field=field,
        input_data=input_data,
        ctx={"reason": reason or f"Authentication failed for {field}"}
    )
    
    return create_http_exception(
        status_code=401,
        message="Ошибка аутентификации",
        errors=[error]
    )


def create_not_found_error(
    field: str,
    message: str,
    input_data: Optional[Any] = None,
    reason: Optional[str] = None
) -> HTTPException:
    """
    Создает ошибку "не найдено" (404 Not Found).
    
    Args:
        field: Поле, которое не найдено
        message: Сообщение об ошибке
        input_data: Значение поля
        reason: Причина ошибки
        
    Returns:
        HTTPException с кодом 404
    """
    error = create_api_error(
        error_type="not_found",
        message=message,
        field=field,
        input_data=input_data,
        ctx={"reason": reason or f"{field} not found"}
    )
    
    return create_http_exception(
        status_code=404,
        message="Ресурс не найден",
        errors=[error]
    )


def create_server_error(
    message: str = "Сервер временно недоступен. Попробуйте позже.",
    reason: Optional[str] = None
) -> HTTPException:
    """
    Создает серверную ошибку (500 Internal Server Error).
    
    Args:
        message: Сообщение об ошибке
        reason: Причина ошибки
        
    Returns:
        HTTPException с кодом 500
    """
    error = create_api_error(
        error_type="server_error",
        message=message,
        field=None,
        input_data=None,
        ctx={"reason": reason or "Internal server error"}
    )
    
    return create_http_exception(
        status_code=500,
        message="Внутренняя ошибка сервера",
        errors=[error]
    )


def create_business_logic_error(
    message: str,
    field: Optional[str] = None,
    input_data: Optional[Any] = None,
    reason: Optional[str] = None
) -> HTTPException:
    """
    Создает ошибку бизнес-логики (400 Bad Request).
    
    Args:
        message: Сообщение об ошибке
        field: Поле, связанное с ошибкой
        input_data: Входные данные
        reason: Причина ошибки
        
    Returns:
        HTTPException с кодом 400
    """
    error = create_api_error(
        error_type="business_error",
        message=message,
        field=field,
        input_data=input_data,
        ctx={"reason": reason or "Business logic error"}
    )
    
    return create_http_exception(
        status_code=400,
        message="Ошибка бизнес-логики",
        errors=[error]
    )


def create_rate_limit_error(
    field: str,
    message: str,
    input_data: Optional[Any] = None,
    retry_after: Optional[int] = None
) -> HTTPException:
    """
    Создает ошибку превышения лимита запросов (429 Too Many Requests).
    
    Args:
        field: Поле, связанное с лимитом
        message: Сообщение об ошибке
        input_data: Входные данные
        retry_after: Время до следующей попытки в секундах
        
    Returns:
        HTTPException с кодом 429
    """
    ctx = {"reason": "Rate limit exceeded"}
    if retry_after:
        ctx["retry_after"] = retry_after
    
    error = create_api_error(
        error_type="rate_limit",
        message=message,
        field=field,
        input_data=input_data,
        ctx=ctx
    )
    
    return create_http_exception(
        status_code=429,
        message="Превышен лимит запросов",
        errors=[error]
    )


def create_forbidden_error(
    field: str,
    message: str,
    input_data: Optional[Any] = None,
    reason: Optional[str] = None
) -> HTTPException:
    """
    Создает ошибку доступа запрещен (403 Forbidden).
    
    Args:
        field: Поле, связанное с ошибкой
        message: Сообщение об ошибке
        input_data: Значение поля
        reason: Причина ошибки
        
    Returns:
        HTTPException с кодом 403
    """
    error = create_api_error(
        error_type="forbidden",
        message=message,
        field=field,
        input_data=input_data,
        ctx={"reason": reason or f"Access forbidden for {field}"}
    )
    
    return create_http_exception(
        status_code=403,
        message="Доступ запрещен",
        errors=[error]
    )