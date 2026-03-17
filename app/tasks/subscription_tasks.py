from app.celery import celery_app
from app.core.logging_config import get_logger
from app.database.core import SessionLocalSync

from app.database.crud.subscription_crud import deactivate_subs

logger = get_logger(__name__)

@celery_app.task(name="subscriptions.deactivate_expired")
def deactivate_expired_subscriptions_task():
    with SessionLocalSync() as session:
        with session.begin():
            count = deactivate_subs(session)

    return count
