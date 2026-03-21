from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import Optional

from app.database.models.tests import Test


async def create_test(
    session: AsyncSession,
    psychologist_id: int,
    title: str,
    public_link_token: str,
    access_until: Optional[datetime] = None,
    client_can_view_report: bool = False
) -> Test:
    test = Test(
        psychologist_id=psychologist_id,
        title=title,
        public_link_token=public_link_token,
        access_until=access_until,
        client_can_view_report=client_can_view_report,
        attempts_count=0
    )
    session.add(test)
    await session.commit()
    await session.refresh(test)
    return test


async def get_test_by_id(session: AsyncSession, test_id: int) -> Optional[Test]:
    result = await session.execute(
        select(Test).where(Test.id == test_id)
    )
    return result.scalars().first()


async def get_test_by_token(session: AsyncSession, token: str) -> Optional[Test]:
    result = await session.execute(
        select(Test).where(Test.public_link_token == token)
    )
    return result.scalars().first()


async def get_tests_by_psychologist(
    session: AsyncSession,
    psychologist_id: int,
    skip: int = 0,
    limit: int = 20
) -> tuple[list[Test], int]:
    count_result = await session.execute(
        select(func.count(Test.id)).where(Test.psychologist_id == psychologist_id)
    )
    total = count_result.scalar() or 0
    
    result = await session.execute(
        select(Test)
        .where(Test.psychologist_id == psychologist_id)
        .order_by(Test.id.desc())
        .offset(skip)
        .limit(limit)
    )
    tests = list(result.scalars().all())
    
    return tests, total


async def update_test(
    session: AsyncSession,
    test_id: int,
    title: Optional[str] = None,
    access_until: Optional[datetime] = None,
    client_can_view_report: Optional[bool] = None
) -> Optional[Test]:
    result = await session.execute(
        select(Test).where(Test.id == test_id)
    )
    test = result.scalars().first()
    
    if not test:
        return None
    
    if title is not None:
        test.title = title
    if access_until is not None:
        test.access_until = access_until
    if client_can_view_report is not None:
        test.client_can_view_report = client_can_view_report
    
    await session.commit()
    await session.refresh(test)
    return test


async def delete_test(session: AsyncSession, test_id: int) -> bool:
    result = await session.execute(
        select(Test).where(Test.id == test_id)
    )
    test = result.scalars().first()
    
    if not test:
        return False
    
    await session.delete(test)
    await session.commit()
    return True


async def increment_attempts_count(session: AsyncSession, test_id: int) -> bool:
    result = await session.execute(
        update(Test)
        .where(Test.id == test_id)
        .values(attempts_count=Test.attempts_count + 1)
    )
    await session.commit()
    return result.rowcount > 0
