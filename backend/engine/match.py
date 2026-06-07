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
    if not last_donation_date:
        return True
    try:
        last = datetime.strptime(last_donation_date[:10], "%Y-%m-%d")
        days_since = (datetime.now() - last).days
        return days_since >= 120
    except:
        return True


COMPATIBLE_DONORS = {
    "O+": ["O+", "O-"],
    "O-": ["O-"],
    "A+": ["A+", "A-", "O+", "O-"],
    "A-": ["A-", "O-"],
    "B+": ["B+", "B-", "O+", "O-"],
    "B-": ["B-", "O-"],
    "AB+": ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
    "AB-": ["A-", "B-", "AB-", "O-"],
    # Handle "Positive/Negative" format
    "O Positive": ["O Positive", "O Negative"],
    "O Negative": ["O Negative"],
    "A Positive": ["A Positive", "A Negative", "O Positive", "O Negative"],
    "A Negative": ["A Negative", "O Negative"],
    "B Positive": ["B Positive", "B Negative", "O Positive", "O Negative"],
    "B Negative": ["B Negative", "O Negative"],
    "AB Positive": ["A Positive", "A Negative", "B Positive", "B Negative", "AB Positive", "AB Negative", "O Positive", "O Negative"],
    "AB Negative": ["A Negative", "B Negative", "AB Negative", "O Negative"],
}


def rank_donors(
    donors: list,
    patient_blood_group: str,
    patient_lat: float,
    patient_lon: float,
    count: int = 20,
) -> list:
    """
    Rank donors using AI-powered response prediction + proximity + compatibility
    """
    # Try to load AI predictor
    try:
        from engine.donor_predictor import predict_donor_response
        use_ai = True
    except:
        use_ai = False

    compatible_groups = COMPATIBLE_DONORS.get(patient_blood_group, [patient_blood_group])
    eligible = [d for d in donors if d.get("blood_group") in compatible_groups and is_eligible(d.get("last_donation_date"))]

    for donor in eligible:
        dist = calculate_distance(patient_lat, patient_lon, donor.get("latitude", 0), donor.get("longitude", 0))
        donor["distance_km"] = round(dist, 1)

        if use_ai:
            # AI-powered prediction
            ai_score = predict_donor_response(donor)

            # Proximity factor (closer = better, max 50km)
            proximity = max(0, 1 - (dist / 50))

            # Final score: 70% AI prediction, 30% proximity
            donor["readiness_score"] = round(ai_score * 0.7 + proximity * 0.3, 3)
            donor["scoring_method"] = "xgboost_ai"
        else:
            # Fallback to rule-based scoring
            ratio = min(donor.get("calls_to_donations_ratio", 0.5), 1.0)
            reliability = min(ratio / max(ratio, 1.0), 1.0) if ratio > 0 else 0.3
            proximity = max(0, 1 - (dist / 50))
            eligibility = 1.0
            willingness = min(donor.get("total_donations", 0) / 10, 1.0)

            donor["readiness_score"] = round(
                eligibility * 0.25 + reliability * 0.30 + proximity * 0.25 + willingness * 0.20, 2
            )
            donor["scoring_method"] = "rule_based"

    eligible.sort(key=lambda d: d["readiness_score"], reverse=True)
    return eligible[:count]
