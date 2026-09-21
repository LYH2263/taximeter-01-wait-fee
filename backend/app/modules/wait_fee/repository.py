import sqlite3
from datetime import datetime, timezone

TABLE = "wait_rules"


class WaitRuleConflict(Exception):
    """同一时刻出现了两条启用规则。a_id / b_id 为冲突双方的标识。"""

    def __init__(self, a_id: int, b_id: int):
        self.a_id = a_id
        self.b_id = b_id
        super().__init__(f"同一时刻只允许一条启用规则：规则 #{a_id} 与规则 #{b_id} 冲突")


class WaitRuleNotFound(LookupError):
    pass


def _row(row: sqlite3.Row) -> dict | None:
    if row is None:
        return None
    d = dict(row)
    d["active"] = bool(d.get("active", 0))
    return d


def list_all(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute(f"SELECT * FROM {TABLE} ORDER BY id").fetchall()
    return [_row(r) for r in rows]


def get(conn: sqlite3.Connection, rule_id: int) -> dict | None:
    return _row(conn.execute(f"SELECT * FROM {TABLE} WHERE id=?", (rule_id,)).fetchone())


def get_active(conn: sqlite3.Connection) -> dict | None:
    return _row(
        conn.execute(f"SELECT * FROM {TABLE} WHERE active=1 ORDER BY id LIMIT 1").fetchone()
    )


def insert(
    conn: sqlite3.Connection, free_min: float, per_min_price: float, active: bool = True
) -> dict:
    """创建规则。若 active 且已存在另一条启用规则，回滚并抛 WaitRuleConflict。"""
    now = datetime.now(timezone.utc).isoformat()
    cur = conn.execute(
        f"INSERT INTO {TABLE}(free_min,per_min_price,active,created_at) VALUES (?,?,?,?)",
        (free_min, per_min_price, 1 if active else 0, now),
    )
    new_id = int(cur.lastrowid)
    if active:
        other = conn.execute(
            f"SELECT id FROM {TABLE} WHERE active=1 AND id<>? ORDER BY id LIMIT 1",
            (new_id,),
        ).fetchone()
        if other is not None:
            conn.rollback()
            raise WaitRuleConflict(new_id, int(other["id"]))
    conn.commit()
    return get(conn, new_id)


def update(conn: sqlite3.Connection, rule_id: int, changes: dict) -> dict:
    """部分更新 free_min / per_min_price / active。

    激活时若另有启用规则，回滚并抛 WaitRuleConflict（点名双方标识）。
    """
    current = get(conn, rule_id)
    if current is None:
        raise WaitRuleNotFound(rule_id)
    free_min = changes.get("free_min", current["free_min"])
    per_min_price = changes.get("per_min_price", current["per_min_price"])
    active = changes.get("active", current["active"])
    conn.execute(
        f"UPDATE {TABLE} SET free_min=?, per_min_price=?, active=? WHERE id=?",
        (free_min, per_min_price, 1 if active else 0, rule_id),
    )
    if active:
        other = conn.execute(
            f"SELECT id FROM {TABLE} WHERE active=1 AND id<>? ORDER BY id LIMIT 1",
            (rule_id,),
        ).fetchone()
        if other is not None:
            conn.rollback()
            raise WaitRuleConflict(rule_id, int(other["id"]))
    conn.commit()
    return get(conn, rule_id)
