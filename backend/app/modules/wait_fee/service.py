"""等候规则业务逻辑：校验、唯一启用约束、增删改查编排。"""
import sqlite3

from app.modules.wait_fee import repository as repo


class RuleNotFound(Exception):
    """规则不存在。"""


class RuleConflict(Exception):
    """同一时刻只允许一条启用规则；报错点名冲突双方标识。"""

    def __init__(self, existing: dict, incoming_label: str, incoming_id: int | None = None):
        self.existing = existing
        incoming = f"#{incoming_id}「{incoming_label}」" if incoming_id is not None else f"新规则「{incoming_label}」"
        super().__init__(
            f"同一时刻只允许一条启用规则：已启用 #{existing['id']}「{existing['label']}」，与{incoming}冲突"
        )


def _validate(free_min: float, per_min: float) -> None:
    if free_min is None or float(free_min) < 0:
        raise ValueError("免费等候分钟不得为负")
    if per_min is None or float(per_min) <= 0:
        raise ValueError("等候每分钟单价必须为正")


def list_rules(conn: sqlite3.Connection) -> list[dict]:
    return repo.list_rules(conn)


def active_rule(conn: sqlite3.Connection) -> dict | None:
    return repo.get_active(conn)


def create_rule(conn: sqlite3.Connection, label: str, free_min: float, per_min: float, active: bool = True) -> dict:
    _validate(free_min, per_min)
    if active:
        existing = repo.get_active(conn)
        if existing:
            raise RuleConflict(existing, label)
    rid = repo.insert(conn, label, free_min, per_min, active)
    return repo.get(conn, rid)


def update_rule(
    conn: sqlite3.Connection,
    rule_id: int,
    *,
    label: str | None = None,
    free_min: float | None = None,
    per_min: float | None = None,
    active: bool | None = None,
) -> dict:
    rule = repo.get(conn, rule_id)
    if not rule:
        raise RuleNotFound(rule_id)
    new_label = rule["label"] if label is None else label
    new_free = rule["free_min"] if free_min is None else float(free_min)
    new_per = rule["per_min"] if per_min is None else float(per_min)
    new_active = rule["active"] if active is None else bool(active)
    _validate(new_free, new_per)
    if new_active:
        existing = repo.get_active(conn)
        if existing and existing["id"] != rule_id:
            raise RuleConflict(existing, new_label, incoming_id=rule_id)
    repo.update(conn, rule_id, new_label, new_free, new_per, new_active)
    return repo.get(conn, rule_id)


def deactivate(conn: sqlite3.Connection, rule_id: int) -> dict:
    rule = repo.get(conn, rule_id)
    if not rule:
        raise RuleNotFound(rule_id)
    repo.update(conn, rule_id, rule["label"], rule["free_min"], rule["per_min"], False)
    return repo.get(conn, rule_id)
