from typing import Optional
from datetime import datetime, timedelta
import math


def calculate_urgency_window(
    last_transfusion_date: str,
    cycle_length_days: int,
    hb_level: Optional[float] = None,
    ferritin_level: Optional[float] = None,
) -> dict:
    last_date = datetime.strptime(last_transfusion_date, "%Y-%m-%d")
    next_transfusion = last_date + timedelta(days=cycle_length_days)
    today = datetime.now()
    days_remaining = math.ceil((next_transfusion - today).total_seconds() / 86400)

    if hb_level is not None:
        if hb_level < 5:
            days_remaining = min(days_remaining, 1)
        elif hb_level < 7:
            days_remaining = max(days_remaining - 3, 1)
        elif hb_level < 9:
            days_remaining = max(days_remaining - 1, 1)

    if ferritin_level is not None and ferritin_level < 15:
        days_remaining = max(days_remaining - 2, 1)

    days_remaining = max(days_remaining, 1)

    if days_remaining <= 3:
        priority = "URGENT"
    elif days_remaining <= 7:
        priority = "MODERATE"
    else:
        priority = "SCHEDULED"

    return {
        "urgency_window_days": days_remaining,
        "priority": priority,
        "next_transfusion_date": next_transfusion.strftime("%Y-%m-%d"),
    }
