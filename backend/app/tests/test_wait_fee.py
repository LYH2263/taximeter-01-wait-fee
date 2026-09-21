import json

import pytest
from fastapi.testclient import TestClient

from app import seed
from app.db import connect
from app.main import app


@pytest.fixture()
def client():
    seed.init_db()
    conn = connect()
    conn.execute("DELETE FROM wait_fee_rules")
    conn.execute("DELETE FROM calc_runs")
    conn.commit()
    conn.close()
    with TestClient(app) as c:
        yield c


def make_rule(client, **kw):
    body = {"label": "标准等候", "free_min": 3, "per_min": 0.5}
    body.update(kw)
    return client.post("/api/wait-fee/rules", json=body)


def run_count():
    conn = connect()
    n = conn.execute("SELECT COUNT(*) c FROM calc_runs").fetchone()["c"]
    conn.close()
    return n


def fare(client, **kw):
    body = {"distance_km": 5, "slow_min": 2, "wait_min": 8, "persist": True}
    body.update(kw)
    return client.post("/api/fare", json=body)


# ---------- 规则 CRUD 与校验 ----------

def test_create_and_list_rules(client):
    r = make_rule(client)
    assert r.status_code == 201
    rule = r.json()
    assert rule["active"] is True and rule["free_min"] == 3 and rule["per_min"] == 0.5
    items = client.get("/api/wait-fee/rules").json()["items"]
    assert [x["id"] for x in items] == [rule["id"]]


def test_free_min_must_not_be_negative(client):
    assert make_rule(client, free_min=-1).status_code == 422
    assert client.get("/api/wait-fee/rules").json()["items"] == []


def test_per_min_must_be_positive(client):
    assert make_rule(client, per_min=0).status_code == 422
    assert make_rule(client, per_min=-0.5).status_code == 422
    assert client.get("/api/wait-fee/rules").json()["items"] == []


def test_update_rule(client):
    rid = make_rule(client).json()["id"]
    r = client.put(f"/api/wait-fee/rules/{rid}", json={"free_min": 5, "per_min": 1.5, "label": "夜间等候"})
    assert r.status_code == 200
    rule = r.json()
    assert rule["free_min"] == 5 and rule["per_min"] == 1.5 and rule["label"] == "夜间等候"
    assert client.put("/api/wait-fee/rules/9999", json={"free_min": 1}).status_code == 404


def test_update_rejects_invalid_values(client):
    rid = make_rule(client).json()["id"]
    assert client.put(f"/api/wait-fee/rules/{rid}", json={"free_min": -2}).status_code == 422
    assert client.put(f"/api/wait-fee/rules/{rid}", json={"per_min": 0}).status_code == 422


def test_deactivate_rule(client):
    rid = make_rule(client).json()["id"]
    r = client.post(f"/api/wait-fee/rules/{rid}/deactivate")
    assert r.status_code == 200 and r.json()["active"] is False
    assert client.post("/api/wait-fee/rules/9999/deactivate").status_code == 404


# ---------- 同一时刻只允许一条启用规则 ----------

def test_only_one_active_rule_on_create(client):
    a = make_rule(client, label="规则甲").json()
    r = make_rule(client, label="规则乙")
    assert r.status_code == 409
    detail = r.json()["detail"]
    assert f"#{a['id']}" in detail and "规则甲" in detail and "规则乙" in detail
    # 显式创建停用规则不冲突
    ok = make_rule(client, label="规则乙", active=False)
    assert ok.status_code == 201 and ok.json()["active"] is False


def test_only_one_active_rule_on_activate(client):
    a = make_rule(client, label="规则甲").json()
    b = make_rule(client, label="规则乙", active=False).json()
    r = client.put(f"/api/wait-fee/rules/{b['id']}", json={"active": True})
    assert r.status_code == 409
    detail = r.json()["detail"]
    assert f"#{a['id']}" in detail and f"#{b['id']}" in detail
    client.post(f"/api/wait-fee/rules/{a['id']}/deactivate")
    assert client.put(f"/api/wait-fee/rules/{b['id']}", json={"active": True}).status_code == 200


# ---------- 打表计入等候费 ----------

def test_fare_includes_wait_fee(client):
    rule = make_rule(client, free_min=3, per_min=0.5).json()
    r = fare(client, distance_km=5, slow_min=2, wait_min=8)
    assert r.status_code == 200
    body = r.json()
    assert body["wait_rule_id"] == rule["id"]
    assert body["wait_billable_min"] == 5  # 8 - 3 免费
    assert body["wait_fee"] == 2.5
    assert body["total"] == round(body["start"] + body["mileage"] + body["slow_fee"] + body["wait_fee"], 2)
    assert body["total"] == 20.1  # 11 + 5.0 + 1.6 + 2.5


def test_billable_min_clamps_at_zero(client):
    make_rule(client, free_min=10, per_min=0.5)
    body = fare(client, wait_min=4).json()
    assert body["wait_billable_min"] == 0 and body["wait_fee"] == 0


def test_negative_wait_min_rejected_without_record(client):
    make_rule(client)
    before = run_count()
    r = fare(client, wait_min=-1)
    assert r.status_code == 422
    assert run_count() == before


def test_readonly_trial_writes_no_record(client):
    make_rule(client)
    before = run_count()
    r = fare(client, persist=False)
    assert r.status_code == 200 and r.json()["run_id"] is None
    assert r.json()["wait_fee"] == 2.5
    assert run_count() == before


def test_fare_without_active_rule_is_zero(client):
    body = fare(client, wait_min=8).json()
    assert body["wait_fee"] == 0 and body["wait_rule_id"] is None


def test_deactivate_then_same_inputs_give_zero_wait_fee(client):
    rule = make_rule(client).json()
    assert fare(client, wait_min=8).json()["wait_fee"] == 2.5
    client.post(f"/api/wait-fee/rules/{rule['id']}/deactivate")
    body = fare(client, wait_min=8).json()
    assert body["wait_fee"] == 0 and body["wait_rule_id"] is None


def test_persisted_record_keeps_rule_snapshot(client):
    rule = make_rule(client, per_min=0.5).json()
    run_id = fare(client, wait_min=8).json()["run_id"]
    client.put(f"/api/wait-fee/rules/{rule['id']}", json={"per_min": 2.0})
    items = client.get("/api/history").json()["items"]
    rec = next(x for x in items if x["id"] == run_id)
    result = json.loads(rec["result_json"])
    assert result["wait_rule_id"] == rule["id"]
    assert result["wait_fee"] == 2.5  # 改单价后不回写历史记录
    # 新订单按新单价计算
    assert fare(client, wait_min=8).json()["wait_fee"] == 10.0
