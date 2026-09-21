import json

# ---- 规则 CRUD ----


def test_create_rule_defaults_active(client):
    r = client.post("/api/wait-rules", json={"free_min": 5, "per_min_price": 1.2})
    assert r.status_code == 201
    body = r.json()
    assert body["id"] > 0
    assert body["free_min"] == 5
    assert body["per_min_price"] == 1.2
    assert body["active"] is True


def test_negative_free_min_rejected(client):
    r = client.post("/api/wait-rules", json={"free_min": -1, "per_min_price": 1.2})
    assert r.status_code == 422


def test_zero_free_min_allowed(client):
    r = client.post("/api/wait-rules", json={"free_min": 0, "per_min_price": 1.0})
    assert r.status_code == 201


def test_price_must_be_positive(client):
    assert client.post("/api/wait-rules", json={"free_min": 3, "per_min_price": 0}).status_code == 422
    assert client.post("/api/wait-rules", json={"free_min": 3, "per_min_price": -2}).status_code == 422


def test_update_price_validation(client):
    rid = client.post("/api/wait-rules", json={"free_min": 3, "per_min_price": 1.0}).json()["id"]
    assert client.patch(f"/api/wait-rules/{rid}", json={"per_min_price": 0}).status_code == 422
    assert client.patch(f"/api/wait-rules/{rid}", json={"free_min": -5}).status_code == 422


def test_list_rules(client):
    client.post("/api/wait-rules", json={"free_min": 5, "per_min_price": 1.0, "active": False})
    client.post("/api/wait-rules", json={"free_min": 3, "per_min_price": 2.0})
    items = client.get("/api/wait-rules").json()["items"]
    assert len(items) == 2
    assert {(x["free_min"], x["active"]) for x in items} == {(5.0, False), (3.0, True)}


def test_update_and_404(client):
    rid = client.post("/api/wait-rules", json={"free_min": 5, "per_min_price": 1.0}).json()["id"]
    r = client.patch(f"/api/wait-rules/{rid}", json={"free_min": 8, "per_min_price": 1.5})
    assert r.status_code == 200
    assert r.json()["free_min"] == 8
    assert r.json()["per_min_price"] == 1.5
    assert client.patch("/api/wait-rules/9999", json={"free_min": 1}).status_code == 404
    assert client.post("/api/wait-rules/9999/disable").status_code == 404


def test_disable_rule(client):
    rid = client.post("/api/wait-rules", json={"free_min": 5, "per_min_price": 1.0}).json()["id"]
    r = client.post(f"/api/wait-rules/{rid}/disable")
    assert r.status_code == 200
    assert r.json()["active"] is False


def test_second_active_rule_conflict_names_both(client):
    a = client.post("/api/wait-rules", json={"free_min": 3, "per_min_price": 1.0}).json()
    r = client.post("/api/wait-rules", json={"free_min": 5, "per_min_price": 2.0})
    assert r.status_code == 409
    detail = r.json()["detail"]
    assert "冲突" in detail
    assert str(a["id"]) in detail
    items = client.get("/api/wait-rules").json()["items"]
    assert len(items) == 1
    assert items[0]["id"] == a["id"]


def test_create_inactive_when_one_active_ok(client):
    client.post("/api/wait-rules", json={"free_min": 3, "per_min_price": 1.0})
    r = client.post("/api/wait-rules", json={"free_min": 5, "per_min_price": 2.0, "active": False})
    assert r.status_code == 201


def test_activate_second_rule_conflict(client):
    a = client.post("/api/wait-rules", json={"free_min": 3, "per_min_price": 1.0}).json()
    b = client.post("/api/wait-rules", json={"free_min": 5, "per_min_price": 2.0, "active": False}).json()
    r = client.patch(f"/api/wait-rules/{b['id']}", json={"active": True})
    assert r.status_code == 409
    detail = r.json()["detail"]
    assert "冲突" in detail
    assert str(a["id"]) in detail
    assert str(b["id"]) in detail
    items = client.get("/api/wait-rules").json()["items"]
    assert [x for x in items if x["id"] == b["id"]][0]["active"] is False


def test_disable_then_activate_other_ok(client):
    a = client.post("/api/wait-rules", json={"free_min": 3, "per_min_price": 1.0}).json()
    b = client.post("/api/wait-rules", json={"free_min": 5, "per_min_price": 2.0, "active": False}).json()
    client.post(f"/api/wait-rules/{a['id']}/disable")
    r = client.patch(f"/api/wait-rules/{b['id']}", json={"active": True})
    assert r.status_code == 200


# ---- 打表 ----


def _make_rule(client, free_min, price):
    return client.post(
        "/api/wait-rules", json={"free_min": free_min, "per_min_price": price}
    ).json()


def test_fare_with_wait_breakdown(client):
    rule = _make_rule(client, 5, 1.0)
    r = client.post(
        "/api/fare",
        json={"distance_km": 5, "slow_min": 2, "wait_min": 10, "persist": False},
    )
    assert r.status_code == 200
    b = r.json()
    assert b["wait_rule_id"] == rule["id"]
    assert b["charged_min"] == 5
    assert b["wait_fee"] == 5.0
    assert b["start"] == 11
    assert b["mileage"] == 5.0
    assert b["slow_fee"] == 1.6
    assert b["total"] == round((((11 + 5.0) + 1.6) + 5.0), 2)


def test_wait_within_free_window_is_zero(client):
    _make_rule(client, 5, 1.0)
    b = client.post(
        "/api/fare",
        json={"distance_km": 1, "slow_min": 0, "wait_min": 4, "persist": False},
    ).json()
    assert b["charged_min"] == 0
    assert b["wait_fee"] == 0.0


def test_negative_wait_min_rejects_entire_order(client):
    def fare_rows():
        return [
            x
            for x in client.get("/api/history").json()["items"]
            if x["kind"] == "fare"
        ]

    before = len(fare_rows())
    r = client.post("/api/fare", json={"distance_km": 5, "slow_min": 2, "wait_min": -3})
    assert r.status_code == 422
    assert len(fare_rows()) == before


def test_read_only_preview_does_not_write_run(client):
    before = client.get("/api/history").json()["items"]
    r = client.post(
        "/api/fare",
        json={"distance_km": 5, "slow_min": 2, "wait_min": 9, "persist": False},
    )
    assert r.status_code == 200
    assert r.json()["run_id"] is None
    after = client.get("/api/history").json()["items"]
    assert after == before


def test_disabled_rule_zero_wait_fee_same_input(client):
    rule = _make_rule(client, 5, 1.0)
    payload = {"distance_km": 5, "slow_min": 2, "wait_min": 10, "persist": False}
    before = client.post("/api/fare", json=payload).json()
    assert [before["wait_fee"] == 5.0, before["wait_rule_id"] == rule["id"]]
    client.post(f"/api/wait-rules/{rule['id']}/disable")
    after = client.post("/api/fare", json=payload).json()
    assert after["wait_rule_id"] is None
    assert after["charged_min"] == 0
    assert after["wait_fee"] == 0.0
    assert after["total"] == round((before["total"] - 5.0), 2)


def test_written_run_keeps_snapshot_after_price_change(client):
    rule = _make_rule(client, 0, 1.0)
    persisted = client.post(
        "/api/fare",
        json={"distance_km": 3, "slow_min": 0, "wait_min": 10, "persist": True},
    ).json()
    rid = persisted["run_id"]
    assert persisted["wait_rule_id"] == rule["id"]
    assert persisted["wait_fee"] == 10.0

    client.patch(f"/api/wait-rules/{rule['id']}", json={"per_min_price": 9.0})
    history = client.get("/api/history").json()["items"]
    row = next(x for x in history if x["id"] == rid)
    result = json.loads(row["result_json"])
    assert result["wait_rule_id"] == rule["id"]
    assert result["wait_fee"] == 10.0
    assert result["charged_min"] == 10


def test_persist_true_writes_run(client):
    r = client.post(
        "/api/fare",
        json={"distance_km": 5, "slow_min": 2, "wait_min": 8, "persist": True},
    ).json()
    rid = r["run_id"]
    assert rid is not None
    history = client.get("/api/history").json()["items"]
    assert any(x["id"] == rid for x in history)


def test_no_rule_at_all_zero_wait_fee(client):
    b = client.post(
        "/api/fare",
        json={"distance_km": 5, "slow_min": 2, "wait_min": 30, "persist": False},
    ).json()
    assert b["wait_rule_id"] is None
    assert b["wait_fee"] == 0.0
    assert b["total"] == round(((b["start"] + b["mileage"]) + b["slow_fee"]), 2)
