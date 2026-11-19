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
    """Allow production deploy only during the actual JST 03:00 hour.

    plan/rollback remain unrestricted. The scheduled run time cannot stand in
    for the trusted real clock. Call at request, before SSH, and server apply.
    """
    if mode != "deploy":
        return None
    instant = now if now is not None else datetime.now(JST)
    date_jst = deploy_jst_date(mode, instant)
    if instant.astimezone(JST).hour != 3:
        raise ValueError("Production deploy is permitted only 03:00–03:59 JST")
    return date_jst
