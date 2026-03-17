from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth_utils import get_user_id_from_token
from app.database.core import get_db
from app.schemas.SubsPlanId import AddSubscriptionRequest
from app.services.subscription_service import (
    get_subscription_plans,
    SubscriptionPlansNotFoundError, subscribe_user, SubscriptionNotFoundError, get_sub, get_subs_all
)
from app.core.dependencies import check_is_admin, ForbiddenError
from app.core.response_utils import (
    create_success_response,
    create_not_found_error,
    create_forbidden_error,
    create_server_error
)
from app.schemas.api_response import SuccessResponse
from app.docs.subscription_responses import SUBSCRIPTION_PLANS_RESPONSES, CURRENT_SUBSCRIPTION_RESPONSES, \
    ADD_SUBSCRIPTION_RESPONSES, HISTORY_RESPONSES
from app.services.user import UserNotFound
from app.core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


@router.get(
    "/plans",
    response_model=SuccessResponse,
    status_code=200,
    responses=SUBSCRIPTION_PLANS_RESPONSES,
    summary="Получить тарифные планы",
    description="Возвращает список активных тарифных планов, разделенных на месячные и годовые"
)
async def get_plans(
    session: AsyncSession = Depends(get_db)
):
    
    try:
        plans = await get_subscription_plans(session)
        
        return create_success_response(
            message="Тарифные планы получены успешно",
            data={"plans": plans}
        )
        
    except SubscriptionPlansNotFoundError as e:
        raise create_not_found_error(
            field=e.field,
            message=e.message,
            input_data="",
            reason="No subscription plans found"
        )
        
    except Exception:
        raise create_server_error()


@router.get(
    "/current",
    response_model=SuccessResponse,
    status_code=200,
    responses=CURRENT_SUBSCRIPTION_RESPONSES,
    summary="Получить текущую подписку пользователя",
    description="Возвращает активную подписку для пользователя, полученного из access токена"
)
async def get_current_subscription(
        request: Request,
        session: AsyncSession = Depends(get_db)
):
    try:
        # Получаем user_id из токена
        user_id = get_user_id_from_token(request)

        # Получаем подписку
        subscription = await get_sub(session, user_id)

        return create_success_response(
            message="Подписка пользователя получена успешно",
            data={
                "subscription": {
                    "id": subscription.id,
                    "plan_id": subscription.plan_id,
                    "user_id": subscription.user_id,
                    "started_at": subscription.started_at.isoformat() if subscription.started_at else None,
                    "expires_at": subscription.expires_at.isoformat() if subscription.expires_at else None,
                    "is_active": subscription.is_active
                }
            }
        )

    except UserNotFound as e:
        raise create_not_found_error(
            field=e.field,
            message=e.message,
            input_data=user_id,
            reason="User not found in database"
        )

    except SubscriptionNotFoundError as e:
        raise create_not_found_error(
            field="subscription",
            message="Подписка пользователя не найдена",
            input_data=user_id,
            reason="Subscription not found"
        )

    except HTTPException:
        raise

    except Exception:
        raise create_server_error()

@router.post(
    "/add",
    response_model=SuccessResponse,
    status_code=200,
    responses=ADD_SUBSCRIPTION_RESPONSES,
    summary="Добавить подписку текущему пользователю",
    description="Добавляет выбранный тариф пользователю, начисляет токены и логирует транзакцию"
)
async def add_subscription(
    request: Request,
    body: AddSubscriptionRequest,
    session: AsyncSession = Depends(get_db)
):
    try:
        # Получаем user_id из токена
        user_id = get_user_id_from_token(request)

        # Выполняем бизнес-логику подписки
        await subscribe_user(
            session=session,
            user_id=user_id,
            plan_id=body.plan_id
        )

        return create_success_response(
            message=f"Подписка успешно добавлена пользователю {user_id}"
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

    except Exception as e:
        logger.error(f"DATABASE ERROR: {e}", exc_info=True)
        raise create_server_error()


@router.get(
    "/history",
    response_model=SuccessResponse,
    status_code=200,
    responses=HISTORY_RESPONSES,
    summary="Получить историю подписок пользователя",
    description="Возвращает все подписки пользователя (активные и завершенные) с информацией о тарифах"
)
async def get_subscription_history(
    request: Request,
    session: AsyncSession = Depends(get_db)
):
    try:
        # Получаем user_id из access токена
        user_id = get_user_id_from_token(request)

        # Получаем все подписки пользователя
        subscriptions = await get_subs_all(session, user_id)

        return create_success_response(
            message="История подписок получена успешно",
            data={
                "subscriptions": [
                    {
                        "subscription_id": sub["subscription_id"],
                        "plan_name": sub["plan_name"],
                        "plan_description": sub["plan_description"],
                        "tokens": sub["tokens"],
                        "duration_days": sub["duration_days"],
                        "started_at": sub["started_at"].isoformat() if sub["started_at"] else None,
                        "expires_at": sub["expires_at"].isoformat() if sub["expires_at"] else None,
                        "is_active": sub["is_active"]
                    }
                    for sub in subscriptions
                ]
            }
        )

    except UserNotFound as e:
        raise create_not_found_error(
            field=e.field,
            message=e.message,
            input_data=user_id,
            reason="User not found in database"
        )

    except SubscriptionNotFoundError:
        raise create_not_found_error(
            field="subscription",
            message="Подписки пользователя не найдены",
            input_data=user_id,
            reason="Subscriptions not found"
        )

    except HTTPException:
        raise

    except Exception:
        raise create_server_error()
