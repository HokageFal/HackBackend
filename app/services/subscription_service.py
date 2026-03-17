from sqlalchemy.ext.asyncio import AsyncSession
from app.database.crud import subsplans_crud, token_crud, subscription_crud
from datetime import datetime, timedelta

from app.database.crud.subscription_crud import get_sub_from_user_id, get_all_subs_from_user
from app.database.crud.user_crud import get_user_by_id
from app.database.models import UserSubscription
from app.database.models.token_ledger import TokenTransactionType
from app.core.logging_config import get_logger
from app.services.user import UserNotFound

logger = get_logger(__name__)

class SubscriptionPlansNotFoundError(Exception):
    def __init__(self, message: str = "Тарифные планы не найдены"):
        self.field = "subscription_plans"
        self.message = message
        super().__init__(message)

class SubscriptionNotFoundError(Exception):
    def __init__(self, message: str = "Тариф не найден"):
        self.field = "user_subscriptions"
        self.message = message
        super().__init__(message)

async def get_subscription_plans(session: AsyncSession) -> dict:
    plans = await subsplans_crud.get_all_active_plans(session)
    
    if not plans:
        raise SubscriptionPlansNotFoundError("Тарифные планы не найдены")

    result  = {"monthly": [], "yearly": []}

    for plan in plans:
        item = {
            "id": plan.id,
            "name": plan.name,
            "description": plan.description,
            "price": plan.price_cents / 100,
            "tokens": plan.tokens_per_period,
            "features": plan.feature_labels or [],
            "duration_days": plan.duration_days
        }

        if plan.duration_days <= 31:
            result["monthly"].append(item)
        elif plan.duration_days >= 365:
            result["yearly"].append(item)

    return result

async def get_sub(
        session: AsyncSession,
        user_id: int
) -> UserSubscription:
    user = await get_user_by_id(session, user_id)

    if not user:
        logger.warning(
            "Subscription failed - user not found",
            operation="subscribe_user",
            user_id=user_id,
            reason="user_not_found"
        )
        raise UserNotFound("id", f"Пользователь с ID {user_id} не найден")

    subscribe = await get_sub_from_user_id(session, user.id)

    if not subscribe:
        logger.warning(
            "Subscription failed - user not found",
            operation="subscribe_user",
            user_id=user_id,
            reason="subscribe_not_found"
        )
        raise SubscriptionNotFoundError()

    return subscribe

async def subscribe_user(
    session: AsyncSession,
    user_id: int,
    plan_id: int
) -> None:
    async with session.begin():
        user = await token_crud.get_user_for_update(session, user_id)
        if user is None:
            logger.warning(
                "Subscription failed - user not found",
                operation="subscribe_user",
                user_id=user_id,
                plan_id=plan_id,
                reason="user_not_found"
            )
            raise UserNotFound("id", f"Пользователь с ID {user_id} не найден")

        plan = await subscription_crud.get_active_plan(session, plan_id)
        if plan is None:
            logger.warning(
                "Subscription failed - plan not found",
                operation="subscribe_user",
                user_id=user_id,
                plan_id=plan_id,
                reason="plan_not_found"
            )
            raise SubscriptionPlansNotFoundError(f"Тариф с ID {plan_id} не найден или не активен")

        await subscription_crud.deactivate_active_subscription(
            session,
            user_id
        )
        logger.info(
            "Deactivated existing subscription (if any)",
            operation="subscribe_user",
            user_id=user_id
        )

        now = datetime.utcnow()
        expires_at = now + timedelta(days=plan.duration_days)
        subscription = subscription_crud.create_user_subscription(
            user_id=user_id,
            plan_id=plan.id,
            started_at=now,
            expires_at=expires_at
        )
        session.add(subscription)
        logger.info(
            "Created new subscription",
            operation="subscribe_user",
            user_id=user_id,
            plan_id=plan.id,
            expires_at=expires_at.isoformat()
        )

        token_crud.add_token_balance(user, plan.tokens_per_period)

        tx = token_crud.create_token_transaction(
            session=session,
            user_id=user_id,
            amount=plan.tokens_per_period,
            transaction_type=TokenTransactionType.subscription,
            description=f"Начисление по подписке «{plan.name}»"
        )
        session.add(tx)
        logger.info(
            "Credited tokens for subscription",
            operation="subscribe_user",
            user_id=user_id,
            plan_id=plan.id,
            tokens=plan.tokens_per_period,
            transaction_id=getattr(tx, "id", None)
        )

        logger.info(
            "User subscription completed successfully",
            operation="subscribe_user",
            user_id=user_id,
            plan_id=plan.id
        )

async def get_subs_all(
        session: AsyncSession,
        user_id: int):
    user = await get_user_by_id(session, user_id)

    if not user:
        logger.warning(
            "Subscription failed - user not found",
            operation="subscribe_user",
            user_id=user.id,
            reason="user_not_found"
        )
        raise UserNotFound("id", f"Пользователь с ID {user_id} не найден")

    subscribes = await get_all_subs_from_user(session, user.id)

    if not subscribes:
        logger.warning(
            "Subscription failed - user not found",
            operation="subscribe_user",
            user_id=user.id,
            reason="subscribe_not_found"
        )
        raise SubscriptionNotFoundError()

    subscriptions = []
    for sub, plan_name, plan_desc, plan_tokens, plan_duration in subscribes.all():
        subscriptions.append({
            "subscription_id": sub.id,
            "plan_name": plan_name,
            "plan_description": plan_desc,
            "tokens": plan_tokens,
            "duration_days": plan_duration,
            "started_at": sub.started_at,
            "expires_at": sub.expires_at,
            "is_active": sub.is_active
        })

    return subscriptions
