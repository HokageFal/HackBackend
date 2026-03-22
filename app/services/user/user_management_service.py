"""
User management service.
Handles user retrieval, deletion, and activation.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging_config import get_logger
from app.database.crud.user_crud import get_user_by_email, get_user_by_id, delete_user_by_id
from app.database.models.users import User
from app.services.user.exceptions import UserNotFound

logger = get_logger(__name__)


async def get_current_user_service(session: AsyncSession, user_id: int) -> User:
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
            full_name=user.full_name,
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
        
        await session.commit()
        
        logger.info(
            "User deleted successfully",
            operation="delete_user_service",
            user_id=user_id,
            email=user.email,
            full_name=user.full_name
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


async def update_user_profile_service(
    session: AsyncSession,
    user_id: int,
    about_markdown: str | None = None,
    photo_url: str | None = None
) -> User:
    logger.info(
        "Starting user profile update",
        operation="update_user_profile_service",
        user_id=user_id
    )
    
    try:
        user = await get_user_by_id(session, user_id)
        
        if user is None:
            logger.warning(
                "User profile update failed - user not found",
                operation="update_user_profile_service",
                user_id=user_id
            )
            raise UserNotFound("id", f"Пользователь с ID {user_id} не найден")
        
        # Обновляем поля
        if about_markdown is not None:
            user.about_markdown = about_markdown
        if photo_url is not None:
            user.photo_url = photo_url
            
        await session.commit()
        await session.refresh(user)
        
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
