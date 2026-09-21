def calc_fare(distance_km: float, slow_min: float, night: bool, tariff: dict, wait: dict | None = None) -> dict:
    base = float(tariff["start_price"])
    include = float(tariff["start_include_km"])
    per_km = float(tariff["per_km"])
    per_slow = float(tariff["per_slow_min"])
    night_f = float(tariff.get("night_factor", 1.0)) if night else 1.0
    dist = max(0.0, float(distance_km) - include)
    mile = dist * per_km
    slow = float(slow_min) * per_slow

    wait = wait or {}
    wait_rule_id = wait.get("wait_rule_id")
    charged_min = float(wait.get("charged_min", 0.0))
    wait_min = float(wait.get("wait_min", 0.0))
    wait_fee = float(wait.get("wait_fee", 0.0))

    start = round(base * night_f, 2)
    mileage = round(mile * night_f, 2)
    slow_fee = round(slow * night_f, 2)
    wait_fee = round(wait_fee, 2)
    total = round(start + mileage + slow_fee + wait_fee, 2)
    return {
        "distance_km": round(float(distance_km), 2),
        "slow_min": round(float(slow_min), 1),
        "wait_min": round(wait_min, 1),
        "night": night,
        "night_factor": night_f,
        "wait_rule_id": wait_rule_id,
        "charged_min": round(charged_min, 1),
        "start": start,
        "mileage": mileage,
        "slow_fee": slow_fee,
        "wait_fee": wait_fee,
        "total": total,
    }
