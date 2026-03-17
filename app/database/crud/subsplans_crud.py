from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import UserSubscription
from app.database.models.subscription_plans import SubscriptionPlan


async def get_all_active_plans(session: AsyncSession) -> list[SubscriptionPlan]:
    result = await session.execute(
        select(SubscriptionPlan)
        .where(SubscriptionPlan.is_active == True)
        .order_by(SubscriptionPlan.duration_days, SubscriptionPlan.price_cents)
    )
    return list(result.scalars().all())


async def get_all_plans(session: AsyncSession) -> list[SubscriptionPlan]:
    """Получить все тарифные планы (включая неактивные)"""
    result = await session.execute(
        select(SubscriptionPlan).order_by(SubscriptionPlan.price_cents)
    )
    return list(result.scalars().all())


async def get_plan_by_id(session: AsyncSession, plan_id: int) -> SubscriptionPlan | None:
    """Получить тарифный план по ID"""
    result = await session.execute(
        select(SubscriptionPlan).where(SubscriptionPlan.id == plan_id)
    )
    return result.scalar_one_or_none()

