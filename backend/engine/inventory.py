from typing import Optional
from datetime import datetime, timedelta


def search_blood_banks(banks: list, blood_group: str, district: Optional[str] = None) -> list:
    results = []
    for bank in banks:
        if district and bank["district"].lower() != district.lower():
            continue
        inv = bank.get("inventory", {}).get(blood_group)
        if inv and inv["units_available"] > 0:
            results.append({
                "bank_id": bank["bank_id"],
                "name": bank["name"],
                "district": bank["district"],
                "units_available": inv["units_available"],
                "expiry_date": inv["expiry_date"],
                "reserved_count": inv["reserved_count"],
            })
    return results


def reserve_units(banks: list, bank_id: str, blood_group: str, units: int) -> Optional[dict]:
    for bank in banks:
        if bank["bank_id"] == bank_id:
            inv = bank.get("inventory", {}).get(blood_group)
            if inv and inv["units_available"] >= units:
                inv["units_available"] -= units
                inv["reserved_count"] += units
                return {
                    "bank_id": bank_id,
                    "blood_group": blood_group,
                    "units_reserved": units,
                    "remaining": inv["units_available"],
                }
    return None


def get_expiring_stock(banks: list, within_days: int = 7) -> list:
    today = datetime.now()
    alerts = []
    for bank in banks:
        for group, inv in bank.get("inventory", {}).items():
            expiry = datetime.strptime(inv["expiry_date"], "%Y-%m-%d")
            days_left = (expiry - today).days
            if 0 < days_left <= within_days and inv["units_available"] > 0:
                alerts.append({
                    "bank_id": bank["bank_id"],
                    "bank_name": bank["name"],
                    "district": bank["district"],
                    "blood_group": group,
                    "units_available": inv["units_available"],
                    "days_until_expiry": days_left,
                })
    return sorted(alerts, key=lambda a: a["days_until_expiry"])
