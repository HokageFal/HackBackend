from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models.users import User, UserRoleEnum
from datetime import date


async def create_psychologist(
    session: AsyncSession,
    full_name: str,
    email: str,
    phone: str,
    password_hash: str,
    access_until: date | None = None
) -> User:
    psychologist = User(
        full_name=full_name,
        email=email,
        phone=phone,
        password=password_hash,
        role=UserRoleEnum.psychologist,
        is_admin=False,
        is_blocked=False,
        access_until=access_until
    )
    
    session.add(psychologist)
    await session.commit()
    await session.refresh(psychologist)
    return psychologist


async def get_all_psychologists(session: AsyncSession) -> list[User]:
    result = await session.execute(
        select(User)
        .where(User.role == UserRoleEnum.psychologist)
        .order_by(User.created_at.desc())
    )
    return list(result.scalars().all())


async def get_psychologist_by_id(session: AsyncSession, psychologist_id: int) -> User | None:
    result = await session.execute(
        select(User).where(
            User.id == psychologist_id,
            User.role == UserRoleEnum.psychologist
        )
    )
    return result.scalars().first()


async def update_psychologist_access(
    session: AsyncSession,
    psychologist_id: int,
    access_until: date | None = None,
    is_blocked: bool | None = None
) -> User | None:
    result = await session.execute(
        select(User).where(User.id == psychologist_id, User.role == UserRoleEnum.psychologist)
    )
    psychologist = result.scalars().first()
    
    if not psychologist:
        return None
    
    if access_until is not None:
        psychologist.access_until = access_until
    
    if is_blocked is not None:
        psychologist.is_blocked = is_blocked
    
    await session.commit()
    await session.refresh(psychologist)
    return psychologist


async def update_psychologist(
    session: AsyncSession,
    psychologist_id: int,
    full_name: str | None = None,
    phone: str | None = None,
    access_until: date | None = None,
    is_blocked: bool | None = None
) -> User | None:
    result = await session.execute(
        select(User).where(
            User.id == psychologist_id,
            User.role == UserRoleEnum.psychologist
        )
    )
    psychologist = result.scalars().first()
    
    if not psychologist:
        return None
    
    if full_name is not None:
        psychologist.full_name = full_name
    
    if phone is not None:
        psychologist.phone = phone
    
    if access_until is not None:
        psychologist.access_until = access_until
    
    if is_blocked is not None:
        psychologist.is_blocked = is_blocked
    
    await session.commit()
    await session.refresh(psychologist)
    return psychologist
