"""
User registration service.
Handles user registration logic.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.core.logging_config import get_logger
from app.database.crud.user_crud import get_user_by_email, create_user
from app.database.models.users import User
from app.schemas.user import UserCreate
from app.services.user.exceptions import UserAlreadyExists, EmailNotVerified

logger = get_logger(__name__)


async def register_user(session: AsyncSession, user_create: UserCreate) -> User:
    """
    Регистрирует нового пользователя.
    
    Args:
        session: Сессия базы данных
        user_create: Данные для создания пользователя
        
    Returns:
        Созданный объект пользователя
        
    Raises:
        UserAlreadyExists: Пользователь с таким email уже существует
        EmailNotVerified: Email уже зарегистрирован, но не подтвержден
    """
    logger.info(
        "Starting user registration",
        operation="register_user",
        email=user_create.email,
        username=user_create.username,
        has_avatar=bool(user_create.avatar_url)
    )
    
    try:
        # Проверяем существование пользователя по email
        existing_user = await get_user_by_email(session, user_create.email)
        
        if existing_user:
            # Если пользователь существует, но email не подтвержден
            if not existing_user.email_verified:
                logger.warning(
                    "User registration failed - email exists but not verified",
                    operation="register_user",
                    email=user_create.email,
                    reason="email_not_verified"
                )
                raise EmailNotVerified(
                    "email",
                    "Пользователь с таким email уже зарегистрирован, но email не подтвержден. "
                    "Проверьте почту и подтвердите регистрацию"
                )
            
            logger.warning(
                "User registration failed - email already exists",
                operation="register_user",
                email=user_create.email,
                reason="email_already_exists"
            )
            raise UserAlreadyExists("email", "Пользователь с таким email уже существует")

        # Хешируем пароль
        hashed_pw = hash_password(user_create.password)
        
        # Создаем пользователя
        user = User(
            username=user_create.username,
            email=user_create.email,
            password=hashed_pw,
            avatar_url=user_create.avatar_url,
            email_verified=user_create.email_verified
        )
        
        created_user = await create_user(session, user)
        
        logger.info(
            "User registration successful",
            operation="register_user",
            user_id=created_user.id,
            email=created_user.email,
            username=created_user.username
        )
        
        return created_user
        
    except (UserAlreadyExists, EmailNotVerified):
        raise
    except Exception as e:
        logger.error(
            "Unexpected error during user registration",
            operation="register_user",
            email=user_create.email,
            username=user_create.username,
            error_type=type(e).__name__,
            error_message=str(e),
            exc_info=True
        )
        raise
