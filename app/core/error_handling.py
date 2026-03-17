"""
DEPRECATED: Этот модуль устарел и будет удален в будущих версиях.
Используйте app.core.response_utils для создания унифицированных ответов API.

Модуль оставлен для обратной совместимости.
"""

import warnings
from fastapi import HTTPException
from typing import List, Any, Optional, Dict
from app.core.response_utils import (
    create_validation_error as new_create_validation_error,
    create_auth_error as new_create_auth_error,
    create_server_error as new_create_server_error,
    create_business_logic_error as new_create_business_logic_error,
    create_not_found_error as new_create_not_found_error,
    create_api_error,
    create_http_exception
)

# Для обратной совместимости со старыми схемами
from app.schemas.error_response import ErrorResponse, ErrorDetail


def _show_deprecation_warning(func_name: str):
    """Показывает предупреждение об устаревшей функции."""
    warnings.warn(
        f"{func_name} is deprecated. Use app.core.response_utils instead.",
        DeprecationWarning,
        stacklevel=3
    )


def create_error_response(
    status_code: int,
    error_type: str,
    loc: List[str],
    msg: str,
    input_data: Any = None,
    ctx: Optional[Dict[str, Any]] = None
) -> HTTPException:
    """
    DEPRECATED: Используйте app.core.response_utils.create_http_exception
    
    Создает HTTPException с унифицированным форматом ошибки.
    """
    _show_deprecation_warning("create_error_response")
    
    # Преобразуем старый формат в новый
    field = loc[-1] if len(loc) > 1 else None
    error = create_api_error(
        error_type=error_type,
        message=msg,
        field=field,
        input_data=input_data,
        ctx=ctx or {}
    )
    
    return create_http_exception(
        status_code=status_code,
        message=msg,
        errors=[error]
    )


def create_validation_error(
    field: str,
    msg: str,
    input_data: Any = None,
    ctx: Optional[Dict[str, Any]] = None
) -> HTTPException:
    """
    DEPRECATED: Используйте app.core.response_utils.create_validation_error
    """
    _show_deprecation_warning("create_validation_error")
    
    reason = ctx.get("reason") if ctx else None
    return new_create_validation_error(
        field=field,
        message=msg,
        input_data=input_data,
        reason=reason
    )


def create_auth_error(
    field: str,
    msg: str,
    input_data: Any = None,
    ctx: Optional[Dict[str, Any]] = None
) -> HTTPException:
    """
    DEPRECATED: Используйте app.core.response_utils.create_auth_error
    """
    _show_deprecation_warning("create_auth_error")
    
    reason = ctx.get("reason") if ctx else None
    return new_create_auth_error(
        field=field,
        message=msg,
        input_data=input_data,
        reason=reason
    )


def create_server_error(
    msg: str = "Сервер временно недоступен. Попробуйте позже.",
    ctx: Optional[Dict[str, Any]] = None
) -> HTTPException:
    """
    DEPRECATED: Используйте app.core.response_utils.create_server_error
    """
    _show_deprecation_warning("create_server_error")
    
    reason = ctx.get("reason") if ctx else None
    return new_create_server_error(message=msg, reason=reason)


def create_business_logic_error(
    msg: str,
    ctx: Optional[Dict[str, Any]] = None
) -> HTTPException:
    """
    DEPRECATED: Используйте app.core.response_utils.create_business_logic_error
    """
    _show_deprecation_warning("create_business_logic_error")
    
    reason = ctx.get("reason") if ctx else None
    return new_create_business_logic_error(
        message=msg,
        reason=reason
    )


def create_not_found_error(
    field: str,
    msg: str,
    input_data: Any = None,
    ctx: Optional[Dict[str, Any]] = None
) -> HTTPException:
    """
    DEPRECATED: Используйте app.core.response_utils.create_not_found_error
    """
    _show_deprecation_warning("create_not_found_error")
    
    reason = ctx.get("reason") if ctx else None
    return new_create_not_found_error(
        field=field,
        message=msg,
        input_data=input_data,
        reason=reason
    )
