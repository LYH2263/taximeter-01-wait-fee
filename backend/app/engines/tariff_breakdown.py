from app.modules.wait_fee.compute import wait_charge


def calc_fare(distance_km: float, slow_min: float, night: bool, tariff: dict,
              wait_min: float = 0.0, wait_rule: dict | None = None) -> dict:
    base = float(tariff["start_price"])
    include = float(tariff["start_include_km"])
    per_km = float(tariff["per_km"])
    per_slow = float(tariff["per_slow_min"])
    night_f = float(tariff.get("night_factor", 1.0)) if night else 1.0
    dist = max(0.0, float(distance_km) - include)
    start = round(base * night_f, 2)
    mileage = round(dist * per_km * night_f, 2)
    slow_fee = round(float(slow_min) * per_slow * night_f, 2)
    billable, wait_fee = wait_charge(wait_min, wait_rule)
    return {
        "distance_km": round(float(distance_km), 2),
        "slow_min": round(float(slow_min), 1),
        "night": night,
        "night_factor": night_f,
        "start": start,
        "mileage": mileage,
        "slow_fee": slow_fee,
        "wait_min": round(float(wait_min), 1),
        "wait_rule_id": wait_rule.get("id") if wait_rule else None,
        "wait_rule_label": wait_rule.get("label") if wait_rule else None,
        "wait_billable_min": billable,
        "wait_fee": wait_fee,
        "total": round(start + mileage + slow_fee + wait_fee, 2),
    }
