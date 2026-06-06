import math
from datetime import datetime, timedelta


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def is_eligible(last_donation_date: str) -> bool:
    last = datetime.strptime(last_donation_date, "%Y-%m-%d")
    days_since = (datetime.now() - last).days
    return days_since >= 120


COMPATIBLE_DONORS = {
    "O+": ["O+", "O-"],
    "O-": ["O-"],
    "A+": ["A+", "A-", "O+", "O-"],
    "A-": ["A-", "O-"],
    "B+": ["B+", "B-", "O+", "O-"],
    "B-": ["B-", "O-"],
    "AB+": ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
    "AB-": ["A-", "B-", "AB-", "O-"],
}


def rank_donors(
    donors: list,
    patient_blood_group: str,
    patient_lat: float,
    patient_lon: float,
    count: int = 20,
) -> list:
    compatible_groups = COMPATIBLE_DONORS.get(patient_blood_group, [patient_blood_group])
    eligible = [d for d in donors if d["blood_group"] in compatible_groups and is_eligible(d["last_donation_date"])]

    for donor in eligible:
        dist = calculate_distance(patient_lat, patient_lon, donor["latitude"], donor["longitude"])
        donor["distance_km"] = round(dist, 1)

        ratio = min(donor.get("calls_to_donations_ratio", 0.5), 1.0)
        reliability = min(ratio / max(ratio, 1.0), 1.0) if ratio > 0 else 0.3
        proximity = max(0, 1 - (dist / 50))
        eligibility = 1.0
        willingness = min(donor.get("total_donations", 0) / 10, 1.0)

        donor["readiness_score"] = round(
            eligibility * 0.25 + reliability * 0.30 + proximity * 0.25 + willingness * 0.20, 2
        )

    eligible.sort(key=lambda d: d["readiness_score"], reverse=True)
    return eligible[:count]
