from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models.users import User, UserRoleEnum
from datetime import datetime
from sqlalchemy import func


async def create_psychologist(
    session: AsyncSession,
    full_name: str,
    email: str,
    phone: str,
    password_hash: str,
    access_until: datetime | None = None
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
    await session.flush()
    # await session.refresh(psychologist)
    return psychologist


async def get_all_psychologists(
    session: AsyncSession,
    skip: int = 0,
    limit: int = 20
) -> tuple[list[User], int]:
    count_result = await session.execute(
        select(User).where(User.role == UserRoleEnum.psychologist)
    )
    total = len(list(count_result.scalars().all()))
    
    result = await session.execute(
        select(User)
        .where(User.role == UserRoleEnum.psychologist)
        .order_by(User.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    psychologists = list(result.scalars().all())
    
    return psychologists, total


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
    access_until: datetime | None = None,
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
    
    await session.flush()
    # await session.refresh(psychologist)
    return psychologist


async def update_psychologist(
    session: AsyncSession,
    psychologist_id: int,
    full_name: str | None = None,
    phone: str | None = None,
    access_until: datetime | None = None,
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
    
    await session.flush()
    # await session.refresh(psychologist)
    return psychologist



async def update_psychologist_profile(
    session: AsyncSession,
    psychologist_id: int,
    about_markdown: str | None = None,
    photo_url: str | None = None
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
    
    if about_markdown is not None:
        psychologist.about_markdown = about_markdown
    
    if photo_url is not None:
        psychologist.photo_url = photo_url
    
    await session.flush()
    # await session.refresh(psychologist)
    return psychologist

