from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
import httpx

from app.database.core import get_db
from app.schemas.github_auth import GitHubAuthRequest
from app.services.github_service import login_github_user
from app.docs.github_responses import GITHUB_AUTH_RESPONSES
from app.schemas.api_response import AuthSuccessResponse
from app.core.response_utils import (
    create_business_logic_error,
    create_auth_success_response,
    create_server_error
)
from app.core.logging_config import get_logger
from app.core.config import settings

logger = get_logger(__name__)

router = APIRouter(prefix="/users/auth", tags=["GitHub OAuth"])


@router.post(
    "/github",
    response_model=AuthSuccessResponse,
    status_code=200,
    responses=GITHUB_AUTH_RESPONSES,
    summary="GitHub OAuth авторизация",
    description="Принимает код авторизации от GitHub и авторизует пользователя"
)
async def auth_github(
    auth_request: GitHubAuthRequest,
    response: Response,
    session: AsyncSession = Depends(get_db)
):
    logger.info("Processing GitHub OAuth code from frontend")
    
    try:
        # 1. Обмениваем code на access_token GitHub
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://github.com/login/oauth/access_token",
                headers={"Accept": "application/json"},
                data={
                    "client_id": settings.GITHUB_CLIENT_ID,
                    "client_secret": settings.GITHUB_CLIENT_SECRET,
                    "code": auth_request.code,
                }
            )
            
            token_data = token_response.json()
            
            if "error" in token_data:
                logger.error(f"GitHub token exchange failed: {token_data.get('error_description')}")
                raise create_business_logic_error(
                    message="Неверный или истекший код авторизации GitHub",
                    field="code",
                    reason=token_data.get("error_description", "Invalid code")
                )
            
            github_access_token = token_data.get("access_token")
            
            if not github_access_token:
                logger.error("No access_token in GitHub response")
                raise create_business_logic_error(
                    message="Не удалось получить токен от GitHub",
                    field="code",
                    reason="No access_token in response"
                )
        
        # 2. Получаем данные пользователя от GitHub
        async with httpx.AsyncClient() as client:
            user_response = await client.get(
                "https://api.github.com/user",
                headers={
                    "Authorization": f"Bearer {github_access_token}",
                    "Accept": "application/json"
                }
            )
            
            if user_response.status_code != 200:
                logger.error(f"GitHub user API failed: {user_response.status_code}")
                raise create_business_logic_error(
                    message="Не удалось получить данные пользователя от GitHub",
                    field="code",
                    reason=f"GitHub API returned {user_response.status_code}"
                )
            
            user_data = user_response.json()
            
            # Если email не пришел, запрашиваем отдельно через /user/emails
            if not user_data.get("email"):
                logger.info("Email not in user data, fetching from /user/emails")
                emails_response = await client.get(
                    "https://api.github.com/user/emails",
                    headers={
                        "Authorization": f"Bearer {github_access_token}",
                        "Accept": "application/json"
                    }
                )
                
                if emails_response.status_code == 200:
                    emails = emails_response.json()
                    # Ищем primary и verified email
                    primary_email = next(
                        (e["email"] for e in emails if e.get("primary") and e.get("verified")),
                        None
                    )
                    if primary_email:
                        user_data["email"] = primary_email
                        logger.info(f"Found primary verified email: {primary_email}")
                    else:
                        logger.warning("No primary verified email found in GitHub account")
                else:
                    logger.warning(f"Failed to fetch emails: {emails_response.status_code}")
        
        logger.info(f"Successfully fetched GitHub user data for: {user_data.get('login')}")
        
        # 3. Аутентифицируем пользователя и получаем токены
        auth_result = await login_github_user(session, user_data, response)
        
        logger.info("Successfully authenticated GitHub user")
        
        # 4. Возвращаем унифицированный ответ
        return create_auth_success_response(
            message="Вход через GitHub выполнен успешно",
            access_token=auth_result["access_token"],
            user_data=auth_result.get("user")
        )
        
    except httpx.HTTPError as e:
        logger.error(f"HTTP error during GitHub OAuth: {str(e)}")
        raise create_server_error()
