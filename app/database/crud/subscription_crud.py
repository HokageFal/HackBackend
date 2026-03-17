# app/database/crud/subscription_crud.py
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.subscription_plans import SubscriptionPlan
from app.database.models.user_subscriptions import UserSubscription


async def get_active_plan(
    session: AsyncSession,
    plan_id: int
) -> SubscriptionPlan | None:
    return await session.scalar(
        select(SubscriptionPlan)
        .where(
            SubscriptionPlan.id == plan_id,
            SubscriptionPlan.is_active.is_(True)
        )
    )

async def get_sub_from_user_id(
        session: AsyncSession,
        user_id: int
) -> UserSubscription | None:
    return await session.scalar(
        select(UserSubscription)
        .where(
            UserSubscription.user_id == user_id,
            UserSubscription.is_active.is_(True)
        )
    )

async def deactivate_active_subscription(
    session: AsyncSession,
    user_id: int
) -> None:
    await session.execute(
        update(UserSubscription)
        .where(
            UserSubscription.user_id == user_id,
            UserSubscription.is_active.is_(True)
        )
        .values(is_active=False)
    )


def create_user_subscription(
    user_id: int,
    plan_id: int,
    started_at,
    expires_at
) -> UserSubscription:
    return UserSubscription(
        user_id=user_id,
        plan_id=plan_id,
        started_at=started_at,
        expires_at=expires_at,
        is_active=True
    )

async def get_all_subs_from_user(
        session: AsyncSession,
        user_id: int
):
    return await session.execute(
        select(
            UserSubscription,
            SubscriptionPlan.name,
            SubscriptionPlan.description,
            SubscriptionPlan.tokens_per_period,
            SubscriptionPlan.duration_days)
        .join(SubscriptionPlan, UserSubscription.plan_id == SubscriptionPlan.id)
        .where(UserSubscription.user_id == user_id)
        .order_by(UserSubscription.started_at.desc())
    )

def deactivate_subs(session) -> int:
    result = session.execute(
        update(UserSubscription)
        .where(
            UserSubscription.is_active.is_(True),
            UserSubscription.expires_at < func.now()
        )
        .values(is_active=False)
    )
    return result.rowcount
