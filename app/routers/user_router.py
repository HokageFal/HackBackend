from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.core import get_db
from app.core.response_utils import (
    create_success_response,
    create_auth_success_response,
    create_user_data_response,
    create_conflict_error,
    create_auth_error,
    create_forbidden_error,
    create_server_error,
    create_not_found_error,
    create_business_logic_error
)
from app.core.auth_utils import get_user_id_from_token
from app.core.dependencies import verify_csrf
from app.docs.responses.user_responses import (
    USER_REGISTER_RESPONSES,
    USER_LOGIN_RESPONSES,
    REFRESH_TOKEN_RESPONSES,
    ACCESS_TOKEN_RESPONSES,
    USER_BY_ID_RESPONSES,
    USER_DELETE_RESPONSES,
    USER_UPDATE_PROFILE_RESPONSES,
    USER_LOGOUT_RESPONSES,
)
from app.schemas.user import UserCreate
from app.schemas.user_update import UserUpdateProfile
from app.schemas.user_login import UserLogin
from app.schemas.api_response import (
    SuccessResponse,
    AuthSuccessResponse,
    UserDataResponse
)
from app.services.user import (
    register_user,
    login_user,
    update_access,
    get_current_user_service,
    delete_user_service,
    update_user_profile_service,
    UserAlreadyExists,
    InvalidCredentials,
    UserNotFound,
    EmailNotVerified
)

router = APIRouter(prefix="/users")


@router.post(
    "/register",
    response_model=SuccessResponse,
    status_code=201,
    responses=USER_REGISTER_RESPONSES,
)
async def register_user_endpoint(user_create: UserCreate, session: AsyncSession = Depends(get_db)):
    try:
        user = await register_user(session, user_create)
        return create_success_response(
            message="Регистрация прошла успешно",
            data={
                "user_id": user.id,
                "email": user.email,
                "username": user.username
            }
        )

    except UserAlreadyExists as e:
        raise create_conflict_error(
            field=e.field,
            message=e.message,
            input_data=getattr(user_create, e.field, ""),
            reason=f"{e.field.title()} already exists"
        )
    
    except EmailNotVerified as e:
        raise create_forbidden_error(
            field=e.field,
            message=e.message,
            input_data=getattr(user_create, e.field, ""),
            reason="Email not verified"
        )

    except Exception:
        raise create_server_error()


@router.post(
    "/login",
    response_model=AuthSuccessResponse,
    status_code=200,
    responses=USER_LOGIN_RESPONSES,
)
async def login_user_endpoint(user_login: UserLogin,
                     response: Response,
                     session: AsyncSession = Depends(get_db)
                     ):
    try:
        tokens = await login_user(session, user_login, response)
        return create_auth_success_response(
            message="Вход выполнен успешно",
            access_token=tokens["access_token"],
            user_data=tokens.get("user")
        )
    except EmailNotVerified as e:
        input_value = getattr(user_login, e.field, "")
        
        raise create_forbidden_error(
            field=e.field,
            message=e.message,
            input_data=input_value,
            reason="Email not verified"
        )
    except InvalidCredentials as e:
        input_value = getattr(user_login, e.field, "")
        # Скрываем пароль в логах
        if e.field == "password":
            input_value = "***"
        
        raise create_auth_error(
            field=e.field,
            message=e.message,
            input_data=input_value,
            reason=f"Invalid {e.field}"
        )


@router.post(
    "/refresh",
    response_model=AuthSuccessResponse,
    status_code=200,
    responses=REFRESH_TOKEN_RESPONSES,
    dependencies=[Depends(verify_csrf)]  # CSRF защита
)
async def refresh_access_token(request: Request, response: Response):
    try:
        tokens = await update_access(request, response)
        return create_auth_success_response(
            message="Токен успешно обновлен",
            access_token=tokens["access_token"]
        )
        
    except InvalidCredentials as e:
        response.delete_cookie(
            key="jwt",
            httponly=True,
            samesite="Strict",
            secure=True
        )
        response.delete_cookie(
            key="csrf_token",
            httponly=False,
            samesite="Strict",
            secure=True
        )
        raise create_auth_error(
            field=e.field,
            message=e.message,
            input_data="***",
            reason=f"Invalid {e.field}"
        )
    
    except Exception:
        raise create_server_error()


@router.get(
    "/me",
    response_model=UserDataResponse,
    status_code=200,
    responses=USER_BY_ID_RESPONSES,
)
async def get_current_user(request: Request, session: AsyncSession = Depends(get_db)):
    try:
        # Получаем ID пользователя из токена
        user_id = get_user_id_from_token(request)
        
        # Получаем пользователя из базы данных
        user = await get_current_user_service(session, user_id)
        
        return create_user_data_response(
            message="Данные пользователя получены успешно",
            user_data={
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "avatar_url": user.avatar_url,
                "token_balance": user.token_balance,
                "is_admin": user.is_admin,
                "created_at": user.created_at.isoformat() if user.created_at else None
            }
        )
        
    except UserNotFound as e:
        raise create_not_found_error(
            field=e.field,
            message=e.message,
            input_data=user_id,
            reason="User not found in database"
        )
        
    except HTTPException:
        raise
        
    except Exception:
        raise create_server_error()


@router.delete(
    "/me",
    response_model=SuccessResponse,
    status_code=200,
    responses=USER_DELETE_RESPONSES,
)
async def delete_current_user(
    request: Request, 
    response: Response,
    session: AsyncSession = Depends(get_db)
):
    try:
        # Получаем ID пользователя из токена
        user_id = get_user_id_from_token(request)
        
        # Удаляем пользователя
        await delete_user_service(session, user_id)
        
        # Удаляем refresh токен из cookies
        response.delete_cookie(
            key="jwt",
            httponly=True,
            samesite="Strict",
            secure=True
        )
        
        # Удаляем CSRF токен из cookies
        response.delete_cookie(
            key="csrf_token",
            httponly=False,
            samesite="Strict",
            secure=True
        )
        
        # Удаляем CSRF токен из cookies
        response.delete_cookie(
            key="csrf_token",
            httponly=False,
            samesite="Strict",
            secure=True
        )
        
        return create_success_response(
            message="Пользователь успешно удален",
            data={"user_id": user_id}
        )
        
    except UserNotFound as e:
        raise create_not_found_error(
            field=e.field,
            message=e.message,
            input_data=user_id,
            reason="User not found in database"
        )
        
    except HTTPException:
        raise
        
    except Exception:
        raise create_server_error()



@router.post(
    "/logout",
    response_model=SuccessResponse,
    status_code=200,
    responses=USER_LOGOUT_RESPONSES,
)
async def logout_user(response: Response):
    response.delete_cookie(
        key="jwt",
        httponly=True,
        samesite="Strict",
        secure=True
    )
    
    return create_success_response(
        message="Выход выполнен успешно",
        data=None
    )


@router.patch(
    "/me",
    response_model=UserDataResponse,
    status_code=200,
    responses=USER_UPDATE_PROFILE_RESPONSES,
)
async def update_current_user_profile(
    user_update: UserUpdateProfile,
    request: Request,
    session: AsyncSession = Depends(get_db)
):
    try:
        # Проверяем, что хотя бы одно поле указано
        if user_update.username is None and user_update.avatar_url is None:
            raise create_business_logic_error(
                message="Необходимо указать хотя бы одно поле для обновления",
                field="body",
                input_data={},
                reason="No fields to update"
            )
        
        # Получаем ID пользователя из токена
        user_id = get_user_id_from_token(request)
        
        # Обновляем профиль
        user = await update_user_profile_service(
            session,
            user_id,
            username=user_update.username,
            avatar_url=user_update.avatar_url
        )
        
        return create_user_data_response(
            message="Профиль успешно обновлен",
            user_data={
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "avatar_url": user.avatar_url,
                "token_balance": user.token_balance,
                "is_admin": user.is_admin,
                "created_at": user.created_at.isoformat() if user.created_at else None
            }
        )
        
    except UserNotFound as e:
        raise create_not_found_error(
            field=e.field,
            message=e.message,
            input_data=user_id,
            reason="User not found in database"
        )
        
    except HTTPException:
        raise
        
    except Exception:
        raise create_server_error()
