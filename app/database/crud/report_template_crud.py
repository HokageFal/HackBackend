from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database.models.report_templates import ReportTemplate
from app.database.models.enums import ReportAudience


async def create_report_template(
    session: AsyncSession,
    test_id: int,
    audience: ReportAudience,
    template_definition: dict
) -> ReportTemplate:
    template = ReportTemplate(
        test_id=test_id,
        audience=audience,
        template_definition=template_definition
    )
    session.add(template)
    await session.flush()
    # await session.refresh(template)
    return template


async def get_report_template(
    session: AsyncSession,
    test_id: int,
    audience: ReportAudience
) -> Optional[ReportTemplate]:
    result = await session.execute(
        select(ReportTemplate).where(
            ReportTemplate.test_id == test_id,
            ReportTemplate.audience == audience
        )
    )
    return result.scalars().first()


async def get_report_templates_by_test(
    session: AsyncSession,
    test_id: int
) -> list[ReportTemplate]:
    result = await session.execute(
        select(ReportTemplate).where(ReportTemplate.test_id == test_id)
    )
    return list(result.scalars().all())


async def update_report_template(
    session: AsyncSession,
    template_id: int,
    template_definition: dict
) -> Optional[ReportTemplate]:
    result = await session.execute(
        select(ReportTemplate).where(ReportTemplate.id == template_id)
    )
    template = result.scalars().first()
    
    if not template:
        return None
    
    template.template_definition = template_definition
    
    await session.flush()
    # await session.refresh(template)
    return template


async def delete_report_template(session: AsyncSession, template_id: int) -> bool:
    result = await session.execute(
        select(ReportTemplate).where(ReportTemplate.id == template_id)
    )
    template = result.scalars().first()
    
    if not template:
        return False
    
    await session.delete(template)
    await session.flush()
    return True

