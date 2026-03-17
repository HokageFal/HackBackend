from sqlalchemy.ext.asyncio import AsyncSession

from app.database.crud.user_crud import get_user_by_email
from app.tasks.email_tasks import send_otp_email_task


async def process_forgot_password(session: AsyncSession, email: str):
    user = await get_user_by_email(email)

    await send_otp_email_task()