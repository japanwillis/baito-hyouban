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


def require_deploy_window(mode, now=None):
    """Compatibility entrypoint: explicit releases are not restricted by hour.

    Scheduled automation chooses 03:00 JST; explicit requests keep their existing
    authorization, plan and daily-publication checks at any hour.
    """
    return deploy_jst_date(mode, now)
