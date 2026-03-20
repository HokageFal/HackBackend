"""
Authentication service.
Handles login, token generation, and token refresh.
"""

import os
import jwt
from datetime import datetime, timedelta
from fastapi import Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from dotenv import load_dotenv

from app.core.security import verify_password
from app.core.logging_config import get_logger
from app.core.csrf_utils import generate_csrf_token, CSRF_COOKIE_NAME
from app.database.crud.user_crud import get_user_by_email
from app.database.models.users import User
from app.schemas.user_login import UserLogin
from app.services.user.exceptions import InvalidCredentials

load_dotenv()
logger = get_logger(__name__)

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY не задан в .env!")
ALGORITHM = "HS256"


def generate_auth_tokens(user: User) -> tuple[str, str]:
    # Access Token
    access_payload = {
        "id": user.id,
        "type": "access",
        "is_admin": user.is_admin,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(minutes=15)
    }
    access_token = jwt.encode(access_payload, SECRET_KEY, algorithm=ALGORITHM)
    
    # Refresh Token
    refresh_payload = {
        "id": user.id,
        "type": "refresh",
        "is_admin": user.is_admin,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(days=15)
    }
    refresh_token = jwt.encode(refresh_payload, SECRET_KEY, algorithm=ALGORITHM)
    
    return access_token, refresh_token



async def login_user(session: AsyncSession, user_login: UserLogin, response: Response) -> dict:
    logger.info(
        "Starting user login",
        operation="login_user",
        email=user_login.email
    )
    
    try:
        # Ищем пользователя по email
        user = await get_user_by_email(session, user_login.email)

        if user is None:
            logger.warning(
                "Login failed - user not found",
                operation="login_user",
                email=user_login.email,
                reason="user_not_found"
            )
            raise InvalidCredentials("email", "Пользователь с таким email не найден")

        # Проверяем пароль
        if not verify_password(user_login.password, user.password):
            logger.warning(
                "Login failed - invalid password",
                operation="login_user",
                user_id=user.id,
                email=user.email,
                reason="invalid_password"
            )
            raise InvalidCredentials("password", "Неверный пароль")

        # Генерируем токены
        access_token, refresh_token = generate_auth_tokens(user)
        
        # Генерируем CSRF токен
        csrf_token = generate_csrf_token()
        
        # Устанавливаем refresh токен в cookie
        response.set_cookie(
            key="jwt",
            value=refresh_token,
            httponly=True,
            samesite="Strict",
            secure=True
        )
        
        # Устанавливаем CSRF токен в cookie
        response.set_cookie(
            key=CSRF_COOKIE_NAME,
            value=csrf_token,
            httponly=False,
            samesite="Strict",
            secure=True
        )

        logger.info(
            "User login successful",
            operation="login_user",
            user_id=user.id,
            email=user.email,
            full_name=user.full_name
        )

        return {
            "access_token": access_token,
            "user": {
                "id": user.id,
                "full_name": user.full_name,
                "email": user.email,
                "phone": user.phone,
                "photo_url": user.photo_url,
                "role": user.role,
                "is_admin": user.is_admin
            }
        }
        
    except InvalidCredentials:
        raise
    except Exception as e:
        logger.error(
            "Unexpected error during user login",
            operation="login_user",
            email=user_login.email,
            error_type=type(e).__name__,
            error_message=str(e),
            exc_info=True
        )
        raise


async def update_access(request: Request, response: Response) -> dict:
    logger.info(
        "Starting access token refresh",
        operation="update_access",
        user_agent=request.headers.get("user-agent"),
        client_ip=request.client.host if request.client else None
    )
    
    try:
        # Получаем refresh токен из кук
        refresh_token = request.cookies.get("jwt")
        
        if not refresh_token:
            logger.warning(
                "Token refresh failed - no refresh token in cookies",
                operation="update_access",
                reason="missing_refresh_token"
            )
            raise InvalidCredentials("cookie", "Refresh токен не найден в куках")
        
        # Декодируем refresh токен
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])

        # Проверяем тип токена
        if payload.get("type") != "refresh":
            logger.warning(
                "Token refresh failed - wrong token type",
                operation="update_access",
                token_type=payload.get("type"),
                reason="wrong_token_type"
            )
            raise InvalidCredentials("token", "Неверный тип токена")

        # Проверяем срок действия
        exp = payload.get("exp")
        if exp and datetime.utcnow().timestamp() > exp:
            logger.warning(
                "Token refresh failed - token expired",
                operation="update_access",
                token_expired_at=datetime.fromtimestamp(exp).isoformat(),
                reason="token_expired"
            )
            raise InvalidCredentials("token", "Refresh токен истек")

        # Извлекаем данные пользователя
        user_id = payload.get("id")
        is_admin = payload.get("is_admin", False)

        if not user_id:
            logger.warning(
                "Token refresh failed - no user ID in token",
                operation="update_access",
                reason="missing_user_id"
            )
            raise InvalidCredentials("token", "ID пользователя не найден в токене")

        # Создаем новые токены
        access_payload = {
            "id": user_id,
            "type": "access",
            "is_admin": is_admin,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(minutes=15)
        }
        new_access_token = jwt.encode(access_payload, SECRET_KEY, algorithm=ALGORITHM)

        refresh_payload = {
            "id": user_id,
            "type": "refresh",
            "is_admin": is_admin,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(days=15)
        }
        new_refresh_token = jwt.encode(refresh_payload, SECRET_KEY, algorithm=ALGORITHM)
        
        # Генерируем новый CSRF токен
        new_csrf_token = generate_csrf_token()

        # Устанавливаем новый refresh токен в куки
        response.set_cookie(
            key="jwt",
            value=new_refresh_token,
            httponly=True,
            samesite="Strict",
            secure=True
        )
        
        # Устанавливаем новый CSRF токен в куки
        response.set_cookie(
            key=CSRF_COOKIE_NAME,
            value=new_csrf_token,
            httponly=False,
            samesite="Strict",
            secure=True
        )

        logger.info(
            "Access token refresh successful",
            operation="update_access",
            user_id=user_id,
            is_admin=is_admin
        )

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "csrf_token": new_csrf_token,  # Возвращаем новый CSRF токен
            "token_type": "bearer"
        }

    except jwt.ExpiredSignatureError:
        logger.warning(
            "Token refresh failed - JWT expired signature",
            operation="update_access",
            reason="jwt_expired_signature"
        )
        raise InvalidCredentials("token", "Refresh токен истек")
    except jwt.InvalidTokenError as e:
        logger.warning(
            "Token refresh failed - invalid JWT token",
            operation="update_access",
            jwt_error=str(e),
            reason="invalid_jwt_token"
        )
        raise InvalidCredentials("token", "Невалидный refresh токен")
    except InvalidCredentials:
        raise
    except Exception as e:
        logger.error(
            "Unexpected error during token refresh",
            operation="update_access",
            error_type=type(e).__name__,
            error_message=str(e),
            exc_info=True
        )
        raise
