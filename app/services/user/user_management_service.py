"""
User management service.
Handles user retrieval, deletion, and activation.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging_config import get_logger
from app.database.crud.user_crud import get_user_by_email, get_user_by_id, delete_user_by_id
from app.database.models.users import User
from app.services.user.exceptions import UserNotFound
from app.database.crud.user_crud import update_user_profile

logger = get_logger(__name__)


async def get_current_user_service(session: AsyncSession, user_id: int) -> User:
    """
    Получает текущего пользователя по ID.
    
    Args:
        session: Сессия базы данных
        user_id: ID пользователя
        
    Returns:
        Объект пользователя
        
    Raises:
        UserNotFound: Пользователь не найден
    """
    logger.info(
        "Starting current user retrieval",
        operation="get_current_user_service",
        user_id=user_id
    )
    
    try:
        user = await get_user_by_id(session, user_id)
        
        if user is None:
            logger.warning(
                "Current user not found",
                operation="get_current_user_service",
                user_id=user_id,
                reason="user_not_found"
            )
            raise UserNotFound("id", f"Пользователь с ID {user_id} не найден")
        
        logger.info(
            "Current user retrieved successfully",
            operation="get_current_user_service",
            user_id=user.id,
            username=user.username,
            email=user.email
        )
        
        return user
        
    except UserNotFound:
        raise
    except Exception as e:
        logger.error(
            "Unexpected error during current user retrieval",
            operation="get_current_user_service",
            user_id=user_id,
            error_type=type(e).__name__,
            error_message=str(e),
            exc_info=True
        )
        raise


async def delete_user_service(session: AsyncSession, user_id: int) -> bool:
    logger.info(
        "Starting user deletion",
        operation="delete_user_service",
        user_id=user_id
    )
    
    try:
        # Проверяем существование пользователя
        user = await get_user_by_id(session, user_id)
        
        if user is None:
            logger.warning(
                "User deletion failed - user not found",
                operation="delete_user_service",
                user_id=user_id,
                reason="user_not_found"
            )
            raise UserNotFound("id", f"Пользователь с ID {user_id} не найден")
        
        # Удаляем пользователя
        deleted = await delete_user_by_id(session, user_id)
        
        if not deleted:
            logger.error(
                "User deletion failed - unexpected error",
                operation="delete_user_service",
                user_id=user_id,
                reason="deletion_failed"
            )
            raise Exception("Не удалось удалить пользователя")
        
        logger.info(
            "User deleted successfully",
            operation="delete_user_service",
            user_id=user_id,
            email=user.email,
            username=user.username
        )
        
        return True
        
    except UserNotFound:
        raise
    except Exception as e:
        logger.error(
            "Unexpected error during user deletion",
            operation="delete_user_service",
            user_id=user_id,
            error_type=type(e).__name__,
            error_message=str(e),
            exc_info=True
        )
        raise


async def activate_user_by_email(session: AsyncSession, email: str) -> User:
    """
    Активирует пользователя после подтверждения OTP кода.
    
    Args:
        session: Сессия базы данных
        email: Email пользователя
        
    Returns:
        Обновленный объект пользователя
        
    Raises:
        UserNotFound: Пользователь не найден
    """
    logger.info(
        "Starting user activation",
        operation="activate_user_by_email",
        email=email
    )
    
    try:
        user = await get_user_by_email(session, email)
        
        if user is None:
            logger.warning(
                "User activation failed - user not found",
                operation="activate_user_by_email",
                email=email,
                reason="user_not_found"
            )
            raise UserNotFound("email", f"Пользователь с email {email} не найден")
        
        # Активируем пользователя
        user.email_verified = True
        await session.commit()
        await session.refresh(user)
        
        logger.info(
            "User activated successfully",
            operation="activate_user_by_email",
            user_id=user.id,
            email=user.email,
            username=user.username
        )
        
        return user
        
    except UserNotFound:
        raise
    except Exception as e:
        logger.error(
            "Unexpected error during user activation",
            operation="activate_user_by_email",
            email=email,
            error_type=type(e).__name__,
            error_message=str(e),
            exc_info=True
        )
        raise



async def update_user_profile_service(
    session: AsyncSession,
    user_id: int,
    username: str | None = None,
    avatar_url: str | None = None
) -> User:
    """
    Обновляет профиль пользователя.
    
    Args:
        session: Сессия базы данных
        user_id: ID пользователя
        username: Новое имя пользователя (опционально)
        avatar_url: Новый URL аватара (опционально)
        
    Returns:
        Обновленный объект пользователя
        
    Raises:
        UserNotFound: Пользователь не найден
    """
    logger.info(
        "Starting user profile update",
        operation="update_user_profile_service",
        user_id=user_id
    )
    
    try:

        user = await update_user_profile(session, user_id, username, avatar_url)
        
        if user is None:
            logger.warning(
                "User profile update failed - user not found",
                operation="update_user_profile_service",
                user_id=user_id
            )
            raise UserNotFound("id", f"Пользователь с ID {user_id} не найден")
        
        logger.info(
            "User profile updated successfully",
            operation="update_user_profile_service",
            user_id=user.id
        )
        
        return user
        
    except UserNotFound:
        raise
    except Exception as e:
        logger.error(
            "Unexpected error during user profile update",
            operation="update_user_profile_service",
            user_id=user_id,
            error_type=type(e).__name__,
            error_message=str(e),
            exc_info=True
        )
        raise
