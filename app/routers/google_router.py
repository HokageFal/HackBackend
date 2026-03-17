from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.core import get_db
from app.schemas.google_auth import GoogleAuthRequest
from app.services.google_service import login_google_user
from app.docs.google_responses import GOOGLE_AUTH_RESPONSES
from app.schemas.api_response import AuthSuccessResponse
from app.core.response_utils import (
    create_business_logic_error,
    create_auth_success_response
)
from app.core.logging_config import get_logger
from app.core.config import settings
from google.oauth2 import id_token
from google.auth.transport import requests

logger = get_logger(__name__)

router = APIRouter(prefix="/users/auth", tags=["Google OAuth"])


@router.post(
    "/google",
    response_model=AuthSuccessResponse,
    status_code=200,
    responses=GOOGLE_AUTH_RESPONSES,
    summary="Google OAuth авторизация",
    description="Принимает Google ID Token от фронтенда и авторизует пользователя"
)
async def auth_google(
    auth_request: GoogleAuthRequest,
    response: Response,
    session: AsyncSession = Depends(get_db)
):
    logger.info("Processing Google OAuth token from frontend")
    
    try:
        # Верифицируем токен от Google
        id_info = id_token.verify_oauth2_token(
            auth_request.token,
            requests.Request(),
            settings.GOOGLE_CLIENT_ID
        )
        
        # Проверяем audience
        if id_info['aud'] != settings.GOOGLE_CLIENT_ID:
            logger.error("Invalid audience in Google token")
            raise create_business_logic_error(
                message="Неверный токен Google",
                field="token",
                reason="Invalid audience"
            )
        
        # Извлекаем данные пользователя
        user_info = {
            "sub": id_info.get('sub'),
            "email": id_info.get('email'),
            "name": id_info.get('name'),
            "picture": id_info.get('picture')
        }
        
        logger.info(f"Successfully verified Google token for: {user_info.get('email')}")
        
        # Аутентифицируем пользователя и получаем токены
        auth_result = await login_google_user(session, user_info, response)
        logger.info("Successfully authenticated Google user")
        
        # Возвращаем унифицированный ответ
        return create_auth_success_response(
            message="Вход через Google выполнен успешно",
            access_token=auth_result["access_token"],
            user_data=auth_result.get("user")
        )
        
    except ValueError as e:
        # Ошибка верификации токена
        logger.error(f"Google token verification failed: {str(e)}")
        raise create_business_logic_error(
            message="Не удалось верифицировать токен Google",
            field="token",
            reason=str(e)
        )
