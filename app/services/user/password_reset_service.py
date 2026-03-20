"""
Password reset service.
Handles password reset requests and verification.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.core.logging_config import get_logger
from app.database.crud.user_crud import get_user_by_email, update_user_password
from app.database.models.users import AuthProviderEnum
from app.services.otp_service import OTPService
from app.tasks.email_tasks import send_password_reset_email_task
from app.services.user.exceptions import UserNotFound, InvalidOperation

logger = get_logger(__name__)


async def request_password_reset(session: AsyncSession, email: str) -> dict:
    """
    Запрос на сброс пароля.
    
    Args:
        session: Сессия базы данных
        email: Email пользователя
        
    Returns:
        Dict с результатом операции
        
    Note:
        Всегда возвращает успех для защиты от перебора email'ов
    """
    logger.info(
        "Password reset requested",
        operation="request_password_reset",
        email=email
    )
    
    try:
        # Проверяем rate limiting
        can_send = await OTPService.check_rate_limit(email)
        if not can_send:
            # Возвращаем успех, но не отправляем email
            logger.warning(
                "Password reset rate limit exceeded",
                operation="request_password_reset",
                email=email
            )
            return {
                "success": True,
                "message": "Если пользователь существует, код отправлен на email"
            }
        
        # Ищем пользователя
        user = await get_user_by_email(session, email)
        
        # Если пользователь не найден - возвращаем успех (защита от перебора)
        if user is None:
            logger.warning(
                "Password reset requested for non-existent user",
                operation="request_password_reset",
                email=email,
                reason="user_not_found"
            )
            return {
                "success": True,
                "message": "Если пользователь существует, код отправлен на email"
            }
        
        # Проверяем, что пользователь использует email авторизацию
        if user.auth_provider != AuthProviderEnum.email:
            logger.warning(
                "Password reset requested for OAuth user",
                operation="request_password_reset",
                email=email,
                auth_provider=user.auth_provider.value,
                reason="oauth_user"
            )
            # Возвращаем успех, но не отправляем email
            return {
                "success": True,
                "message": "Если пользователь существует, код отправлен на email"
            }
        
        # Генерируем OTP код
        otp_code = OTPService.generate_otp_code()
        
        # Сохраняем код в Redis
        await OTPService.save_otp_code(email, otp_code)
        
        # Отправляем email через Celery
        send_password_reset_email_task.delay(
            email=email,
            username=user.username,
            otp_code=otp_code
        )
        
        logger.info(
            "Password reset code sent successfully",
            operation="request_password_reset",
            email=email,
            user_id=user.id
        )
        
        return {
            "success": True,
            "message": "Если пользователь существует, код отправлен на email"
        }
        
    except Exception as e:
        logger.error(
            "Failed to request password reset",
            operation="request_password_reset",
            email=email,
            error_type=type(e).__name__,
            error_message=str(e),
            exc_info=True
        )
        # Возвращаем успех даже при ошибке (защита от перебора)
        return {
            "success": True,
            "message": "Если пользователь существует, код отправлен на email"
        }


async def reset_password(
    session: AsyncSession,
    email: str,
    code: str,
    new_password: str
) -> dict:
    logger.info(
        "Password reset verification started",
        operation="reset_password",
        email=email
    )
    
    # Проверяем OTP код
    result = await OTPService.verify_otp_code(email, code)
    
    if not result["success"]:
        logger.warning(
            "Password reset failed - invalid OTP",
            operation="reset_password",
            email=email,
            reason=result["message"]
        )
        return result
    
    # Ищем пользователя
    user = await get_user_by_email(session, email)
    
    if user is None:
        logger.warning(
            "Password reset failed - user not found",
            operation="reset_password",
            email=email,
            reason="user_not_found"
        )
        raise UserNotFound("email", f"Пользователь с email {email} не найден")

    if user.auth_provider != AuthProviderEnum.email:
        logger.warning(
            "Password reset failed - OAuth user",
            operation="reset_password",
            email=email,
            user_id=user.id,
            auth_provider=user.auth_provider.value,
            reason="oauth_user"
        )
        raise InvalidOperation(
            "auth_provider",
            f"Невозможно сбросить пароль для пользователя с авторизацией через {user.auth_provider.value}"
        )
    
    # Хэшируем новый пароль
    new_password_hash = hash_password(new_password)
    
    # Обновляем пароль
    success = await update_user_password(session, email, new_password_hash)
    
    if not success:
        logger.error(
            "Password reset failed - database update failed",
            operation="reset_password",
            email=email,
            user_id=user.id
        )
        return {
            "success": False,
            "message": "Не удалось обновить пароль"
        }
    
    logger.info(
        "Password reset successful",
        operation="reset_password",
        email=email,
        user_id=user.id
    )
    
    return {
        "success": True,
        "message": "Пароль успешно изменен"
    }

    
