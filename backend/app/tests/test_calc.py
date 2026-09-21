from app.engines.night_compare import compare_day_night
from app.engines.tariff_breakdown import calc_fare

T = {"start_price": 11, "start_include_km": 3, "per_km": 2.5, "per_slow_min": 0.8, "night_factor": 1.2}
RULE = {"id": 7, "label": "标准等候", "free_min": 3, "per_min": 0.5, "active": True}

def test_day_short():
    r = calc_fare(5, 2, False, T)
    assert r["total"] == 17.6
    assert r["mileage"] == 5.0

def test_night_long():
    r = calc_fare(18, 12, True, T)
    assert r["total"] == 69.72

def test_compare_delta():
    c = compare_day_night(18, 12, T)
    assert c["night_total"] > c["day_total"]

def test_wait_fee_billable():
    r = calc_fare(5, 2, False, T, wait_min=8, wait_rule=RULE)
    assert r["wait_billable_min"] == 5
    assert r["wait_fee"] == 2.5
    assert r["wait_rule_id"] == 7
    assert r["total"] == round(r["start"] + r["mileage"] + r["slow_fee"] + r["wait_fee"], 2)

def test_wait_fee_clamps_at_zero():
    r = calc_fare(5, 2, False, T, wait_min=2, wait_rule=RULE)
    assert r["wait_billable_min"] == 0 and r["wait_fee"] == 0

def test_wait_fee_no_rule():
    r = calc_fare(5, 2, False, T, wait_min=8)
    assert r["wait_fee"] == 0 and r["wait_rule_id"] is None

def test_wait_min_negative_raises():
    import pytest
    with pytest.raises(ValueError):
        calc_fare(5, 2, False, T, wait_min=-1, wait_rule=RULE)
