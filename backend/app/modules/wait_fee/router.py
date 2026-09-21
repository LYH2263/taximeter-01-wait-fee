from fastapi import APIRouter, HTTPException

from app.db import connect
from app.modules.wait_fee import service
from app.modules.wait_fee.schemas import WaitRuleCreate, WaitRuleUpdate

router = APIRouter(prefix="/wait-fee/rules", tags=["wait_fee"])


def _run(fn, *args, **kwargs):
    conn = connect()
    try:
        return fn(conn, *args, **kwargs)
    except service.RuleNotFound as e:
        raise HTTPException(404, f"等候规则不存在: {e}")
    except service.RuleConflict as e:
        raise HTTPException(409, str(e))
    except ValueError as e:
        raise HTTPException(400, str(e))
    finally:
        conn.close()


@router.get("")
def list_rules():
    return {"items": _run(service.list_rules)}


@router.post("", status_code=201)
def create_rule(body: WaitRuleCreate):
    return _run(service.create_rule, body.label, body.free_min, body.per_min, body.active)


@router.put("/{rule_id}")
def update_rule(rule_id: int, body: WaitRuleUpdate):
    return _run(
        service.update_rule,
        rule_id,
        label=body.label,
        free_min=body.free_min,
        per_min=body.per_min,
        active=body.active,
    )


@router.post("/{rule_id}/deactivate")
def deactivate_rule(rule_id: int):
    return _run(service.deactivate, rule_id)
