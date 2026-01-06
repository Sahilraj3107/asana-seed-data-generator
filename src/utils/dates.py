from datetime import datetime, timedelta, timezone
import random

def now_utc() -> datetime:
    return datetime.now(timezone.utc)

def random_past_datetime(history_days: int) -> datetime:
    end = now_utc()
    start = end - timedelta(days=history_days)
    delta = end - start
    return start + timedelta(seconds=random.randint(0, int(delta.total_seconds())))

def iso_ts(dt: datetime) -> str:
    return dt.isoformat(timespec="seconds")

def iso_date(dt: datetime) -> str:
    return dt.date().isoformat()
