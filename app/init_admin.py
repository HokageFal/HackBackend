import logging
import secrets
import string
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.core.security import hash_password
from app.database.models.users import User, UserRoleEnum

logger = logging.getLogger(__name__)

def init_admin():
    try:
        sync_db_url = settings.DATABASE_URL.replace("+asyncpg", "")
        engine = create_engine(sync_db_url, echo=False)
        Session = sessionmaker(bind=engine)

        with Session() as session:
            result = session.execute(select(User).where(User.role == UserRoleEnum.admin))
            existing_admin = result.scalars().first()

            if existing_admin:
                logger.info(f"Администратор существует: {existing_admin.email}")
                return

            admin_email = generate_admin_email()
            admin_password = generate_random_password(16)
            admin_full_name = "Главный Администратор"
            admin_phone = f"+7{''.join(secrets.choice(string.digits) for _ in range(10))}"
            hashed_password = hash_password(admin_password)

            admin = User(
                full_name=admin_full_name,
                email=admin_email,
                phone=admin_phone,
                password=hashed_password,
                role=UserRoleEnum.admin,
                is_admin=True,
                is_blocked=False
            )

            session.add(admin)
            session.commit()
            session.refresh(admin)

            logger.info("=" * 70)
            logger.info("АДМИНИСТРАТОР СОЗДАН!")
            logger.info("=" * 70)
            logger.info(f"Email:    {admin_email}")
            logger.info(f"Пароль:   {admin_password}")
            logger.info(f"ФИО:      {admin_full_name}")
            logger.info(f"Телефон:  {admin_phone}")
            logger.info(f"ID:       {admin.id}")
            logger.info("=" * 70)
            logger.info("СОХРАНИТЕ ЭТИ ДАННЫЕ!")
            logger.info("=" * 70)

        engine.dispose()
    except Exception as e:
        logger.error(f"Ошибка инициализации админа: {e}", exc_info=True)