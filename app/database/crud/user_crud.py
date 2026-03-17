from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.users import User, AuthProviderEnum


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    result = await session.execute(select(User).where(User.email == email))
    return result.scalars().first()


async def get_user_by_username(session: AsyncSession, username: str) -> User | None:
    result = await session.execute(select(User).where(User.username == username))
    return result.scalars().first()


async def create_user(session: AsyncSession, user: User) -> User:
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def get_user_by_id(session: AsyncSession, user_id: int) -> User | None:
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalars().first()


async def check_email_exists(session: AsyncSession, email: str) -> bool:
    result = await session.execute(select(User).where(User.email == email))
    return result.scalars().first() is not None


async def get_user_by_google_id(session: AsyncSession, google_id: str) -> User | None:
    result = await session.execute(select(User).where(User.google_id == google_id))
    return result.scalars().first()


async def update_user_google_data(
        session: AsyncSession, user: User, google_id: str, avatar_url: str | None
) -> User:
    user.google_id = google_id
    if avatar_url:
        user.avatar_url = avatar_url

    user.auth_provider = AuthProviderEnum.google
    user.email_verified = True

    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def get_user_by_tg_id(session: AsyncSession, tg_id: str) -> User | None:
    query = select(User).where(User.telegram_id == tg_id)
    result = await session.execute(query)
    return result.scalars().first()


async def get_user_by_github_id(session: AsyncSession, github_id: str) -> User | None:
    query = select(User).where(User.github_id == github_id)
    result = await session.execute(query)
    return result.scalars().first()


async def update_user_github_data(
        session: AsyncSession, user: User, github_id: str, avatar_url: str | None
) -> User:
    user.github_id = github_id
    if avatar_url:
        user.avatar_url = avatar_url

    user.auth_provider = AuthProviderEnum.github
    user.email_verified = True

    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def delete_user_by_id(session: AsyncSession, user_id: int) -> bool:
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    
    if user is None:
        return False
    
    await session.delete(user)
    await session.commit()
    return True


async def update_user_profile(
    session: AsyncSession,
    user_id: int,
    username: str | None = None,
    avatar_url: str | None = None
) -> User | None:
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    
    if user is None:
        return None
    
    if username is not None:
        user.username = username
    
    if avatar_url is not None:
        user.avatar_url = avatar_url
    
    await session.commit()
    await session.refresh(user)
    return user


async def update_user_password(
    session: AsyncSession,
    email: str,
    new_password_hash: str
) -> bool:
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    
    if user is None:
        return False



    user.password = new_password_hash
    await session.commit()
    return True
