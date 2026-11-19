"""JST date handling for production deployment safeguards."""
from datetime import datetime
from zoneinfo import ZoneInfo

JST = ZoneInfo("Asia/Tokyo")


def deploy_jst_date(mode, now=None):
    if mode != "deploy":
        return None
    instant = now if now is not None else datetime.now(JST)
    if instant.tzinfo is None or instant.utcoffset() is None:
        raise ValueError("Explicit timezone is required for a deploy")
    return instant.astimezone(JST).strftime("%Y-%m-%d")
