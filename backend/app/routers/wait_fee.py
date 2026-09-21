from fastapi import APIRouter, HTTPException

from app.modules.wait_fee import repository as wait_repo
from app.modules.wait_fee.schemas import WaitRuleCreate, WaitRuleUpdate
from app.services.taxi_service import TaxiService

router = APIRouter(prefix="/wait-rules", tags=["wait_fee"])


@router.get("")
def list_rules():
    with TaxiService() as s:
        return {"items": s.list_wait_rules()}


@router.post("", status_code=201)
def create_rule(body: WaitRuleCreate):
    try:
        with TaxiService() as s:
            return s.create_wait_rule(body.free_min, body.per_min_price, body.active)
    except wait_repo.WaitRuleConflict as e:
        raise HTTPException(
            status_code=409,
            detail=f"同一时刻只允许一条启用规则：规则 #{e.a_id} 与规则 #{e.b_id} 冲突",
        )


@router.patch("/{rule_id}")
def update_rule(rule_id: int, body: WaitRuleUpdate):
    try:
        with TaxiService() as s:
            return s.update_wait_rule(rule_id, body.model_dump(exclude_unset=True))
    except wait_repo.WaitRuleNotFound:
        raise HTTPException(status_code=404, detail=f"规则 #{rule_id} 不存在")
    except wait_repo.WaitRuleConflict as e:
        raise HTTPException(
            status_code=409,
            detail=f"同一时刻只允许一条启用规则：规则 #{e.a_id} 与规则 #{e.b_id} 冲突",
        )


@router.post("/{rule_id}/disable")
def disable_rule(rule_id: int):
    try:
        with TaxiService() as s:
            return s.disable_wait_rule(rule_id)
    except wait_repo.WaitRuleNotFound:
        raise HTTPException(status_code=404, detail=f"规则 #{rule_id} 不存在")
