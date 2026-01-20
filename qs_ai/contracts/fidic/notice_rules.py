# qs_ai/contracts/fidic/notice_rules.py
from datetime import timedelta


NOTICE_PERIOD_DAYS = 28


def notice_valid(event) -> bool:
    if not event["notified"]:
        return False

    delta = event["notification_date"] - event["start_date"]
    return delta <= timedelta(days=NOTICE_PERIOD_DAYS)
