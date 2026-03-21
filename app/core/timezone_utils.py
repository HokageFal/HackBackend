from datetime import datetime, timezone, timedelta

MSK_TIMEZONE = timezone(timedelta(hours=3))


def convert_to_msk_naive(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    
    if dt.tzinfo is None:
        return dt
    
    msk_dt = dt.astimezone(MSK_TIMEZONE)
    return msk_dt.replace(tzinfo=None)


def get_current_msk_time() -> datetime:
    return datetime.now(MSK_TIMEZONE).replace(tzinfo=None)
