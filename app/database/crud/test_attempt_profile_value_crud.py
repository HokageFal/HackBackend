from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, datetime
from typing import Optional
from decimal import Decimal

from app.database.models.test_attempt_profile_values import TestAttemptProfileValue


async def create_profile_value(
    session: AsyncSession,
    attempt_id: int,
    profile_field_id: int,
    text_value: Optional[str] = None,
    number_value: Optional[Decimal] = None,
    date_value: Optional[date] = None,
    datetime_value: Optional[datetime] = None
) -> TestAttemptProfileValue:
    value = TestAttemptProfileValue(
        attempt_id=attempt_id,
        profile_field_id=profile_field_id,
        text_value=text_value,
        number_value=number_value,
        date_value=date_value,
        datetime_value=datetime_value
    )
    session.add(value)
    await session.flush()
    # await session.refresh(value)
    return value


async def get_profile_values_by_attempt(
    session: AsyncSession,
    attempt_id: int
) -> list[TestAttemptProfileValue]:
    result = await session.execute(
        select(TestAttemptProfileValue)
        .where(TestAttemptProfileValue.attempt_id == attempt_id)
    )
    return list(result.scalars().all())

