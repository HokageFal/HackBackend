from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database.models.test_profile_fields import TestProfileField
from app.database.models.enums import ProfileFieldType


async def create_profile_field(
    session: AsyncSession,
    test_id: int,
    label: str,
    field_type: ProfileFieldType,
    is_required: bool,
    position: int
) -> TestProfileField:
    field = TestProfileField(
        test_id=test_id,
        label=label,
        type=field_type,
        is_required=is_required,
        position=position
    )
    session.add(field)
    await session.commit()
    await session.refresh(field)
    return field


async def get_profile_fields_by_test(
    session: AsyncSession,
    test_id: int
) -> list[TestProfileField]:
    result = await session.execute(
        select(TestProfileField)
        .where(TestProfileField.test_id == test_id)
        .order_by(TestProfileField.position)
    )
    return list(result.scalars().all())


async def update_profile_field(
    session: AsyncSession,
    field_id: int,
    label: Optional[str] = None,
    field_type: Optional[ProfileFieldType] = None,
    is_required: Optional[bool] = None,
    position: Optional[int] = None
) -> Optional[TestProfileField]:
    result = await session.execute(
        select(TestProfileField).where(TestProfileField.id == field_id)
    )
    field = result.scalars().first()
    
    if not field:
        return None
    
    if label is not None:
        field.label = label
    if field_type is not None:
        field.type = field_type
    if is_required is not None:
        field.is_required = is_required
    if position is not None:
        field.position = position
    
    await session.commit()
    await session.refresh(field)
    return field


async def delete_profile_field(session: AsyncSession, field_id: int) -> bool:
    result = await session.execute(
        select(TestProfileField).where(TestProfileField.id == field_id)
    )
    field = result.scalars().first()
    
    if not field:
        return False
    
    await session.delete(field)
    await session.commit()
    return True
