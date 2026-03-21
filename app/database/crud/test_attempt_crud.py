from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import Optional

from app.database.models.test_attempts import TestAttempt


async def create_attempt(
    session: AsyncSession,
    test_id: int,
    client_name: str
) -> TestAttempt:
    attempt = TestAttempt(
        test_id=test_id,
        client_name=client_name,
        started_at=datetime.utcnow()
    )
    session.add(attempt)
    await session.flush()
    # await session.refresh(attempt)
    return attempt


async def get_attempt_by_id(
    session: AsyncSession,
    attempt_id: int
) -> Optional[TestAttempt]:
    result = await session.execute(
        select(TestAttempt).where(TestAttempt.id == attempt_id)
    )
    return result.scalars().first()


async def get_attempts_by_test(
    session: AsyncSession,
    test_id: int,
    skip: int = 0,
    limit: int = 20
) -> tuple[list[TestAttempt], int]:
    count_result = await session.execute(
        select(func.count(TestAttempt.id)).where(TestAttempt.test_id == test_id)
    )
    total = count_result.scalar() or 0
    
    result = await session.execute(
        select(TestAttempt)
        .where(TestAttempt.test_id == test_id)
        .order_by(TestAttempt.started_at.desc())
        .offset(skip)
        .limit(limit)
    )
    attempts = list(result.scalars().all())
    
    return attempts, total


async def submit_attempt(
    session: AsyncSession,
    attempt_id: int
) -> Optional[TestAttempt]:
    result = await session.execute(
        select(TestAttempt).where(TestAttempt.id == attempt_id)
    )
    attempt = result.scalars().first()
    
    if not attempt:
        return None
    
    attempt.submitted_at = datetime.utcnow()
    
    await session.flush()
    # await session.refresh(attempt)
    return attempt


async def delete_attempt(session: AsyncSession, attempt_id: int) -> bool:
    result = await session.execute(
        select(TestAttempt).where(TestAttempt.id == attempt_id)
    )
    attempt = result.scalars().first()
    
    if not attempt:
        return False
    
    await session.delete(attempt)
    await session.flush()
    return True

