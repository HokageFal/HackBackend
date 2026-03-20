from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging_config import get_logger
from app.core.security import hash_password
from app.core.email_utils import send_email_sync, create_psychologist_credentials_email_template
from app.database.crud.psychologist_crud import (
    create_psychologist,
    get_all_psychologists,
    get_psychologist_by_id,
    update_psychologist
)
from app.database.crud.user_crud import check_email_exists
from app.database.models.users import User
from app.schemas.psychologist import PsychologistCreate
from app.services.user.exceptions import UserAlreadyExists, UserNotFound

logger = get_logger(__name__)


async def create_psychologist_service(
    session: AsyncSession,
    psychologist_data: PsychologistCreate
) -> User:
    logger.info(
        "Starting psychologist creation",
        operation="create_psychologist_service",
        email=psychologist_data.email,
        full_name=psychologist_data.full_name
    )
    
    try:
        email_exists = await check_email_exists(session, psychologist_data.email)
        
        if email_exists:
            logger.warning(
                "Psychologist creation failed - email already exists",
                operation="create_psychologist_service",
                email=psychologist_data.email,
                reason="email_already_exists"
            )
            raise UserAlreadyExists("email", f"Пользователь с email {psychologist_data.email} уже существует")
        
        password_hash = hash_password(psychologist_data.password)
        
        psychologist = await create_psychologist(
            session=session,
            full_name=psychologist_data.full_name,
            email=psychologist_data.email,
            phone=psychologist_data.phone,
            password_hash=password_hash,
            access_until=psychologist_data.access_until
        )
        
        logger.info(
            "Psychologist created successfully",
            operation="create_psychologist_service",
            psychologist_id=psychologist.id,
            email=psychologist.email
        )
        
        if psychologist_data.send_email:
            try:
                email_body = create_psychologist_credentials_email_template(
                    full_name=psychologist_data.full_name,
                    email=psychologist_data.email,
                    password=psychologist_data.password,
                    access_until=psychologist_data.access_until.isoformat() if psychologist_data.access_until else None
                )
                
                send_email_sync(
                    to_email=psychologist_data.email,
                    subject="Добро пожаловать в ПрофДНК - Данные для входа",
                    body=email_body,
                    is_html=True
                )
                
                logger.info(
                    "Credentials email sent successfully",
                    operation="create_psychologist_service",
                    psychologist_id=psychologist.id,
                    email=psychologist.email
                )
            except Exception as e:
                logger.error(
                    "Failed to send credentials email",
                    operation="create_psychologist_service",
                    psychologist_id=psychologist.id,
                    email=psychologist.email,
                    error_type=type(e).__name__,
                    error_message=str(e),
                    exc_info=True
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


async def get_psychologist_by_id_service(
    session: AsyncSession,
    psychologist_id: int
) -> User:
    logger.info(
        "Starting psychologist retrieval",
        operation="get_psychologist_by_id_service",
        psychologist_id=psychologist_id
    )
    
    try:
        psychologist = await get_psychologist_by_id(session, psychologist_id)
        
        if not psychologist:
            logger.warning(
                "Psychologist not found",
                operation="get_psychologist_by_id_service",
                psychologist_id=psychologist_id,
                reason="psychologist_not_found"
            )
            raise UserNotFound("psychologist_id", f"Психолог с ID {psychologist_id} не найден")
        
        logger.info(
            "Psychologist retrieved successfully",
            operation="get_psychologist_by_id_service",
            psychologist_id=psychologist.id,
            email=psychologist.email
        )
        
        return psychologist
        
    except UserNotFound:
        raise
    except Exception as e:
        logger.error(
            "Unexpected error during psychologist retrieval",
            operation="get_psychologist_by_id_service",
            psychologist_id=psychologist_id,
            error_type=type(e).__name__,
            error_message=str(e),
            exc_info=True
        )
        raise


async def get_all_psychologists_service(session: AsyncSession) -> list[User]:
    logger.info(
        "Starting psychologists list retrieval",
        operation="get_all_psychologists_service"
    )
    
    try:
        psychologists = await get_all_psychologists(session)
        
        logger.info(
            "Psychologists list retrieved successfully",
            operation="get_all_psychologists_service",
            count=len(psychologists)
        )
        
        return psychologists
        
    except Exception as e:
        logger.error(
            "Unexpected error during psychologists list retrieval",
            operation="get_all_psychologists_service",
            error_type=type(e).__name__,
            error_message=str(e),
            exc_info=True
        )
        raise



async def update_psychologist_service(
    session: AsyncSession,
    psychologist_id: int,
    update_data: dict
) -> User:
    logger.info(
        "Starting psychologist update",
        operation="update_psychologist_service",
        psychologist_id=psychologist_id,
        fields=list(update_data.keys())
    )
    
    try:
        psychologist = await get_psychologist_by_id(session, psychologist_id)
        
        if not psychologist:
            logger.warning(
                "Psychologist update failed - not found",
                operation="update_psychologist_service",
                psychologist_id=psychologist_id,
                reason="psychologist_not_found"
            )
            raise UserNotFound("psychologist_id", f"Психолог с ID {psychologist_id} не найден")
        
        updated_psychologist = await update_psychologist(
            session=session,
            psychologist_id=psychologist_id,
            full_name=update_data.get("full_name"),
            phone=update_data.get("phone"),
            access_until=update_data.get("access_until"),
            is_blocked=update_data.get("is_blocked")
        )
        
        logger.info(
            "Psychologist updated successfully",
            operation="update_psychologist_service",
            psychologist_id=psychologist_id,
            updated_fields=list(update_data.keys())
        )
        
        return updated_psychologist
        
    except (UserNotFound, UserAlreadyExists):
        raise
    except Exception as e:
        logger.error(
            "Unexpected error during psychologist update",
            operation="update_psychologist_service",
            psychologist_id=psychologist_id,
            error_type=type(e).__name__,
            error_message=str(e),
            exc_info=True
        )
        raise
