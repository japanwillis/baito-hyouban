"""Fail-closed JST window for an explicitly approved production deploy.

Plans never modify the public site and can run outside the publication window.
Manual rollback uses its existing exact-backup approval and is not a new publish.
"""
from datetime import datetime
from zoneinfo import ZoneInfo

JST = ZoneInfo("Asia/Tokyo")


def require_deploy_window(mode, now=None):
    if mode != "deploy":
        return None
    instant = now if now is not None else datetime.now(JST)
    if instant.tzinfo is None or instant.utcoffset() is None:
        raise ValueError("Explicit timezone is required for a deploy")
    local = instant.astimezone(JST)
    if local.hour != 3:
        raise ValueError("Production deploy allowed only at JST 03:00-03:59")
    return local.strftime("%Y-%m-%d")
