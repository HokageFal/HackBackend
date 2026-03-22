from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database.models.test_metrics import TestMetric


async def create_metric(
    session: AsyncSession,
    test_id: int,
    name: str,
    formula: str
) -> TestMetric:
    metric = TestMetric(
        test_id=test_id,
        name=name,
        formula=formula
    )
    session.add(metric)
    await session.flush()
    # await session.refresh(metric)
    return metric


async def get_metrics_by_test(
    session: AsyncSession,
    test_id: int
) -> list[TestMetric]:
    result = await session.execute(
        select(TestMetric).where(TestMetric.test_id == test_id)
    )
    return list(result.scalars().all())


async def update_metric(
    session: AsyncSession,
    metric_id: int,
    name: Optional[str] = None,
    formula: Optional[str] = None
) -> Optional[TestMetric]:
    result = await session.execute(
        select(TestMetric).where(TestMetric.id == metric_id)
    )
    metric = result.scalars().first()
    
    if not metric:
        return None
    
    if name is not None:
        metric.name = name
    if formula is not None:
        metric.formula = formula
    
    await session.flush()
    # await session.refresh(metric)
    return metric


async def delete_metric(session: AsyncSession, metric_id: int) -> bool:
    result = await session.execute(
        select(TestMetric).where(TestMetric.id == metric_id)
    )
    metric = result.scalars().first()
    
    if not metric:
        return False
    
    await session.delete(metric)
    await session.flush()
    return True

