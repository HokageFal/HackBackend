"""
Psychologist service.
Handles psychologist creation and management by admin.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date

from app.core.logging_config import get_logger
from app.core.security import hash_password
from app.core.email_utils import send_email_sync, create_psychologist_credentials_email_template
from app.database.crud.user_crud import get_user_by_email
from app.database.crud.psychologist_crud import create_psychologist
from app.schemas.psychologist import PsychologistCreate
from app.database.models.users import User
from app.services.user.exceptions import UserAlreadyExists

logger = get_logger(__name__)


async def create_psychologist_service(
    session: AsyncSession,
    psychologist_data: PsychologistCreate
) -> User:
    """
    Создает нового психолога (только для админа).
    
    Args:
        session: Сессия базы данных
        psychologist_data: анные для создания психолога
        
    Returns:
        Созданный объект психолога
        
    Raises:
        UserAlreadyExists: ользователь с таким email уже существует
    """
    logger.info(
        "Starting psychologist creation",
        operation="create_psychologist_service",
        email=psychologist_data.email,
        full_name=psychologist_data.full_name
    )
    
    try:
        # роверяем существование пользователя по email
        existing_user = await get_user_by_email(session, psychologist_data.email)
        
        if existing_user:
            logger.warning(
                "Psychologist creation failed - email already exists",
                operation="create_psychologist_service",
                email=psychologist_data.email,
                reason="email_already_exists"
            )
            raise UserAlreadyExists("email", "ользователь с таким email уже существует")
        
        # Хешируем пароль
        hashed_password = hash_password(psychologist_data.password)
        
        # Создаем психолога
        psychologist = await create_psychologist(
            session=session,
            full_name=psychologist_data.full_name,
            email=psychologist_data.email,
            phone=psychologist_data.phone,
            password_hash=hashed_password,
            access_until=psychologist_data.access_until
        )
        
        logger.info(
            "Psychologist created successfully",
            operation="create_psychologist_service",
            psychologist_id=psychologist.id,
            email=psychologist.email,
            full_name=psychologist.full_name,
            access_until=psychologist.access_until.isoformat() if psychologist.access_until else None
        )
        
        # тправляем email с данными доступа, если требуется
        if psychologist_data.send_email:
            try:
                logger.info(
                    " Т EMAIL",
                    operation="create_psychologist_service",
                    psychologist_id=psychologist.id,
                    email=psychologist.email,
                    send_email_flag=psychologist_data.send_email
                )
                
                email_body = create_psychologist_credentials_email_template(
                    full_name=psychologist_data.full_name,
                    email=psychologist_data.email,
                    password=psychologist_data.password,
                    access_until=psychologist_data.access_until.isoformat() if psychologist_data.access_until else None
                )
                
                logger.info(
                    "EMAIL Ш С, ТЯ...",
                    operation="create_psychologist_service",
                    to_email=psychologist_data.email
                )
                
                send_email_sync(
                    to_email=psychologist_data.email,
                    subject="обро пожаловать в роф - анные для входа",
                    body=email_body,
                    is_html=True
                )
                
                logger.info(
                    "EMAIL СШ Т!",
                    operation="create_psychologist_service",
                    psychologist_id=psychologist.id,
                    email=psychologist.email
                )
            except Exception as email_error:
                logger.error(
                    "Ш Т EMAIL",
                    operation="create_psychologist_service",
                    psychologist_id=psychologist.id,
                    email=psychologist.email,
                    error_type=type(email_error).__name__,
                    error_message=str(email_error),
                    exc_info=True
                )
        else:
            logger.info(
                "Т EMAIL Щ (send_email=False)",
                operation="create_psychologist_service",
                psychologist_id=psychologist.id,
                send_email_flag=psychologist_data.send_email
            )
        
        return psychologist
        
    except UserAlreadyExists:
        raise
    except Exception as e:
        logger.error(
            "Unexpected error during psychologist creation",
            operation="create_psychologist_service",
            email=psychologist_data.email,
            error_type=type(e).__name__,
            error_message=str(e),
            exc_info=True
        )
        raise
