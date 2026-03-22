from fastapi import APIRouter, Depends, Request, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
import os
import uuid
from pathlib import Path
from typing import Optional

from app.database.core import get_db
from app.core.dependencies import get_current_psychologist, AccessDeniedError
from app.core.response_utils import (
    create_success_response,
    create_forbidden_error,
    create_server_error,
    create_not_found_error,
    create_business_logic_error,
    create_user_data_response
)
from app.schemas.api_response import SuccessResponse, UserDataResponse
from app.services.psychologist_service import update_psychologist_profile_service
from app.services.user.exceptions import UserNotFound
from app.core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/psychologist", tags=["Psychologist Profile"])


@router.patch(
    "/me",
    response_model=UserDataResponse,
    summary="Обновить свой профиль",
    description="Психолог может обновить описание о себе и/или загрузить фото"
)
async def update_my_profile(
    request: Request,
    session: AsyncSession = Depends(get_db),
    about_markdown: Optional[str] = Form(None, max_length=5000, description="Описание в Markdown"),
    photo: Optional[UploadFile] = File(None, description="Фото профиля")
):
    logger.info(
        "Update psychologist profile endpoint called",
        operation="update_my_profile",
        has_about=about_markdown is not None,
        has_photo=photo is not None
    )
    
    try:
        psychologist = await get_current_psychologist(request, session)
        
        if about_markdown is None and photo is None:
            raise create_business_logic_error(
                message="Необходимо указать хотя бы одно поле для обновления",
                field="body",
                input_data={},
                reason="No fields to update"
            )
        
        photo_url = None
        
        if photo is not None:
            allowed_types = ["image/jpeg", "image/png", "image/jpg", "image/webp"]
            if photo.content_type not in allowed_types:
                raise create_business_logic_error(
                    message="Недопустимый формат файла. Разрешены: JPEG, PNG, WEBP",
                    field="photo",
                    input_data=photo.content_type,
                    reason="Invalid file type"
                )
            
            content = await photo.read()
            if len(content) > 5 * 1024 * 1024:
                raise create_business_logic_error(
                    message="Размер файла не должен превышать 5MB",
                    field="photo",
                    input_data=f"{len(content)} bytes",
                    reason="File too large"
                )
            
            upload_dir = Path("static/uploads/photos")
            upload_dir.mkdir(parents=True, exist_ok=True)
            
            file_ext = photo.filename.split(".")[-1]
            filename = f"{psychologist.id}_{uuid.uuid4().hex}.{file_ext}"
            file_path = upload_dir / filename
            
            with open(file_path, "wb") as f:
                f.write(content)
            
            photo_url = f"/static/uploads/photos/{filename}"
        
        updated_psychologist = await update_psychologist_profile_service(
            session=session,
            psychologist_id=psychologist.id,
            about_markdown=about_markdown,
            photo_url=photo_url
        )
        
        logger.info(
            "Psychologist profile updated successfully",
            operation="update_my_profile",
            psychologist_id=psychologist.id,
            updated_about=about_markdown is not None,
            updated_photo=photo is not None
        )
        
        return create_user_data_response(
            message="Профиль успешно обновлен",
            user_data={
                "id": updated_psychologist.id,
                "full_name": updated_psychologist.full_name,
                "email": updated_psychologist.email,
                "phone": updated_psychologist.phone,
                "photo_url": updated_psychologist.photo_url,
                "about_markdown": updated_psychologist.about_markdown,
                "role": updated_psychologist.role,
                "access_until": updated_psychologist.access_until.isoformat() if updated_psychologist.access_until else None,
                "is_blocked": updated_psychologist.is_blocked,
                "is_admin": updated_psychologist.is_admin,
                "created_at": updated_psychologist.created_at.isoformat() if updated_psychologist.created_at else None
            }
        )
    
    except AccessDeniedError as e:
        logger.warning(
            "Access denied in update profile",
            operation="update_my_profile",
            field=e.field,
            message=e.message
        )
        raise create_forbidden_error(
            field=e.field,
            message=e.message,
            input_data="",
            reason="Access denied"
        )
    
    except UserNotFound as e:
        logger.warning(
            "Psychologist not found error",
            operation="update_my_profile",
            field=e.field,
            message=e.message
        )
        raise create_not_found_error(
            field=e.field,
            message=e.message,
            input_data="",
            reason="Psychologist not found"
        )
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        
        logger.error(
            "Unexpected error in update profile endpoint",
            operation="update_my_profile",
            error_type=type(e).__name__,
            error_message=str(e),
            exc_info=True
        )
        raise create_server_error()


@router.delete(
    "/me/photo",
    response_model=UserDataResponse,
    summary="Удалить фото профиля",
    description="Психолог может удалить свою фотографию"
)
async def delete_my_photo(
    request: Request,
    session: AsyncSession = Depends(get_db)
):
    logger.info(
        "Delete psychologist photo endpoint called",
        operation="delete_my_photo"
    )
    
    try:
        psychologist = await get_current_psychologist(request, session)
        
        updated_psychologist = await update_psychologist_profile_service(
            session=session,
            psychologist_id=psychologist.id,
            photo_url=None
        )
        
        logger.info(
            "Psychologist photo deleted successfully",
            operation="delete_my_photo",
            psychologist_id=psychologist.id
        )
        
        return create_user_data_response(
            message="Фото успешно удалено",
            user_data={
                "id": updated_psychologist.id,
                "full_name": updated_psychologist.full_name,
                "email": updated_psychologist.email,
                "phone": updated_psychologist.phone,
                "photo_url": updated_psychologist.photo_url,
                "about_markdown": updated_psychologist.about_markdown,
                "role": updated_psychologist.role,
                "access_until": updated_psychologist.access_until.isoformat() if updated_psychologist.access_until else None,
                "is_blocked": updated_psychologist.is_blocked,
                "is_admin": updated_psychologist.is_admin,
                "created_at": updated_psychologist.created_at.isoformat() if updated_psychologist.created_at else None
            }
        )
    
    except AccessDeniedError as e:
        logger.warning(
            "Access denied in delete photo",
            operation="delete_my_photo",
            field=e.field,
            message=e.message
        )
        raise create_forbidden_error(
            field=e.field,
            message=e.message,
            input_data="",
            reason="Access denied"
        )
    
    except UserNotFound as e:
        logger.warning(
            "Psychologist not found error",
            operation="delete_my_photo",
            field=e.field,
            message=e.message
        )
        raise create_not_found_error(
            field=e.field,
            message=e.message,
            input_data="",
            reason="Psychologist not found"
        )
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        
        logger.error(
            "Unexpected error in delete photo endpoint",
            operation="delete_my_photo",
            error_type=type(e).__name__,
            error_message=str(e),
            exc_info=True
        )
        raise create_server_error()



@router.get(
    "/me/card",
    response_model=SuccessResponse,
    summary="Получить информацию о своей визитке",
    description="""
    Возвращает информацию о визитке психолога и ссылки для QR кода.
    
    **Возвращает:**
    - URL публичной визитки
    - URL для скачивания QR кода
    - Превью данных визитки
    
    **Использование:**
    - Психолог может посмотреть как выглядит его визитка
    - Получить QR код для печати
    - Поделиться ссылкой с клиентами
    """
)
async def get_my_card_info(
    request: Request,
    session: AsyncSession = Depends(get_db)
):
    from app.core.config import settings
    
    logger.info(
        "Get my card info endpoint called",
        operation="get_my_card_info"
    )
    
    try:
        psychologist = await get_current_psychologist(request, session)
        
        frontend_url = settings.FRONTEND_URL or "http://localhost:3000"
        base_url = settings.BASE_URL or "http://localhost:8000"
        
        card_url = f"{frontend_url}/psychologist/{psychologist.id}"
        qr_url = f"{base_url}/public/psychologist/{psychologist.id}/qr"
        public_api_url = f"{base_url}/public/psychologist/{psychologist.id}/card"
        
        photo_url = None
        if psychologist.photo:
            photo_url = f"{base_url}/static/uploads/photos/{psychologist.photo}"
        
        result = {
            "card_url": card_url,
            "qr_code_url": qr_url,
            "public_api_url": public_api_url,
            "preview": {
                "id": psychologist.id,
                "full_name": psychologist.full_name,
                "email": psychologist.email,
                "phone": psychologist.phone,
                "photo_url": photo_url,
                "about": psychologist.about or ""
            }
        }
        
        logger.info(
            "Card info retrieved successfully",
            operation="get_my_card_info",
            psychologist_id=psychologist.id
        )
        
        return create_success_response(
            message="Информация о визитке",
            data=result
        )
    
    except AccessDeniedError as e:
        logger.warning(
            "Access denied in get card info",
            operation="get_my_card_info",
            field=e.field,
            message=e.message
        )
        raise create_forbidden_error(
            field=e.field,
            message=e.message,
            input_data="",
            reason="Access denied"
        )
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        
        logger.error(
            "Unexpected error in get card info endpoint",
            operation="get_my_card_info",
            error_type=type(e).__name__,
            error_message=str(e),
            exc_info=True
        )
        raise create_server_error()
