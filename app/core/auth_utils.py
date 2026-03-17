from app.core.logging_config import get_logger
import os
import jwt
from fastapi import Request
from app.core.error_handling import create_auth_error, create_not_found_error
from dotenv import load_dotenv

load_dotenv()
logger = get_logger(__name__)

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY не задан в .env! Добавьте SECRET_KEY для безопасной работы приложения.")
ALGORITHM = "HS256"


def get_user_id_from_token(request: Request) -> int:
    try:
        # Получаем токен из заголовка Authorization
        access = request.headers.get("Authorization")
        
        if not access:
            logger.warning(
                "Token extraction failed - no Authorization header",
                operation="get_user_id_from_token",
                reason="missing_authorization_header"
            )
            raise create_not_found_error(
                field="Authorization",
                msg="Токен не найден в заголовке Authorization",
                input_data=None,
                ctx={"reason": "Missing Authorization header"}
            )
        
        # Проверяем формат Bearer токена
        if access.split()[0] != "Bearer":
            logger.warning(
                "Token extraction failed - invalid token format",
                operation="get_user_id_from_token",
                token_format=access.split()[0] if access.split() else "empty",
                reason="invalid_token_format"
            )
            raise create_auth_error(
                field="Authorization",
                msg="Неверный формат токена. Ожидается 'Bearer <token>'",
                input_data=access.split()[0] if access.split() else "",
                ctx={"reason": "Invalid token format"}
            )
        
        # Извлекаем токен
        try:
            token = access.split()[1]
        except IndexError:
            logger.warning(
                "Token extraction failed - empty token",
                operation="get_user_id_from_token",
                reason="empty_token"
            )
            raise create_auth_error(
                field="Authorization",
                msg="Токен не найден после 'Bearer'",
                input_data="",
                ctx={"reason": "Empty token"}
            )
        
        # Декодируем токен
        try:
            decode_access = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except jwt.ExpiredSignatureError:
            logger.warning(
                "Token extraction failed - token expired",
                operation="get_user_id_from_token",
                reason="token_expired"
            )
            raise create_auth_error(
                field="token",
                msg="Access токен истек",
                input_data="***",
                ctx={"reason": "Token expired"}
            )
        except jwt.InvalidTokenError as e:
            logger.warning(
                "Token extraction failed - invalid token",
                operation="get_user_id_from_token",
                jwt_error=str(e),
                reason="invalid_token"
            )
            raise create_auth_error(
                field="token",
                msg="Невалидный access токен",
                input_data="***",
                ctx={"reason": "Invalid token"}
            )
        
        # Проверяем тип токена
        if decode_access.get("type") != "access":
            logger.warning(
                "Token extraction failed - wrong token type",
                operation="get_user_id_from_token",
                token_type=decode_access.get("type"),
                reason="wrong_token_type"
            )
            raise create_auth_error(
                field="token",
                msg="Неверный тип токена. Ожидается access токен",
                input_data="***",
                ctx={"reason": "Wrong token type"}
            )
        
        # Извлекаем user_id
        user_id = decode_access.get("id")
        if not user_id:
            logger.warning(
                "Token extraction failed - no user ID in token",
                operation="get_user_id_from_token",
                reason="missing_user_id"
            )
            raise create_auth_error(
                field="token",
                msg="ID пользователя не найден в токене",
                input_data="***",
                ctx={"reason": "Missing user ID"}
            )
        
        logger.info(
            "User ID extracted successfully",
            operation="get_user_id_from_token",
            user_id=user_id,
            token_expires_at=decode_access.get("exp")
        )
        
        return user_id
        
    except Exception as e:
        # Если это уже HTTPException, перебрасываем его
        if hasattr(e, 'status_code'):
            raise e
        
        # Для любых других ошибок выбрасываем ошибку авторизации
        raise create_auth_error(
            field="token",
            msg="Ошибка при получении ID пользователя из токена",
            input_data="***",
            ctx={"reason": "Token parsing error"}
        )
