from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database.models.test_sections import TestSection


async def create_section(
    session: AsyncSession,
    test_id: int,
    title: str,
    display_order: Optional[int] = None
) -> TestSection:
    section = TestSection(
        test_id=test_id,
        title=title,
        position=display_order or 0
    )
    session.add(section)
    await session.flush()
    return section


async def get_sections_by_test(
    session: AsyncSession,
    test_id: int
) -> list[TestSection]:
    result = await session.execute(
        select(TestSection)
        .where(TestSection.test_id == test_id)
        .order_by(TestSection.position)
    )
    return list(result.scalars().all())


async def update_section(
    session: AsyncSession,
    section_id: int,
    title: Optional[str] = None,
    position: Optional[int] = None
) -> Optional[TestSection]:
    result = await session.execute(
        select(TestSection).where(TestSection.id == section_id)
    )
    section = result.scalars().first()
    
    if not section:
        return None
    
    if title is not None:
        section.title = title
    if position is not None:
        section.position = position
    
    await session.flush()
    # await session.refresh(section)
    return section


async def delete_section(session: AsyncSession, section_id: int) -> bool:
    result = await session.execute(
        select(TestSection).where(TestSection.id == section_id)
    )
    section = result.scalars().first()
    
    if not section:
        return False
    
    await session.delete(section)
    await session.flush()
    return True

