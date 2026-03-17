"""
CSRF protection utilities.
"""

import secrets
from fastapi import Request, HTTPException
from app.core.logging_config import get_logger

logger = get_logger(__name__)

CSRF_TOKEN_LENGTH = 32
CSRF_COOKIE_NAME = "csrf_token"
CSRF_HEADER_NAME = "X-CSRF-Token"


def generate_csrf_token() -> str:
    """
    Генерирует криптографически безопасный CSRF токен.
    
    Returns:
        Случайная строка длиной 32 символа
    """
    return secrets.token_urlsafe(CSRF_TOKEN_LENGTH)


def verify_csrf_token(request: Request) -> bool:
    """
    Проверяет CSRF токен из заголовка и cookie.
    
    Args:
        request: FastAPI Request объект
        
    Returns:
        True если токены совпадают
        
    Raises:
        HTTPException: Если токены не совпадают или отсутствуют
    """
    # Получаем токен из cookie
    csrf_cookie = request.cookies.get(CSRF_COOKIE_NAME)
    
    # Получаем токен из заголовка
    csrf_header = request.headers.get(CSRF_HEADER_NAME)
    
    # Проверяем наличие обоих токенов
    if not csrf_cookie:
        logger.warning(
            "CSRF validation failed - no token in cookie",
            operation="verify_csrf_token"
        )
        raise HTTPException(
            status_code=403,
            detail={
                "message": "CSRF токен не найден в cookie",
                "errors": [{
                    "type": "csrf_error",
                    "field": "cookie",
                    "msg": "CSRF токен отсутствует в cookie",
                    "ctx": {"reason": "Missing CSRF cookie"}
                }]
            }
        )
    
    if not csrf_header:
        logger.warning(
            "CSRF validation failed - no token in header",
            operation="verify_csrf_token"
        )
        raise HTTPException(
            status_code=403,
            detail={
                "message": "CSRF токен не найден в заголовке",
                "errors": [{
                    "type": "csrf_error",
                    "field": "header",
                    "msg": "CSRF токен отсутствует в заголовке X-CSRF-Token",
                    "ctx": {"reason": "Missing CSRF header"}
                }]
            }
        )
    
    # Сравниваем токены (constant-time comparison для защиты от timing attacks)
    if not secrets.compare_digest(csrf_cookie, csrf_header):
        logger.warning(
            "CSRF validation failed - tokens do not match",
            operation="verify_csrf_token"
        )
        raise HTTPException(
            status_code=403,
            detail={
                "message": "CSRF токены не совпадают",
                "errors": [{
                    "type": "csrf_error",
                    "field": "token",
                    "msg": "CSRF токен из cookie не совпадает с токеном из заголовка",
                    "ctx": {"reason": "CSRF token mismatch"}
                }]
            }
        )
    
    logger.debug(
        "CSRF validation successful",
        operation="verify_csrf_token"
    )
    
    return True
