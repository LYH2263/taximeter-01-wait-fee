import sqlite3


def _row(r: sqlite3.Row) -> dict:
    d = dict(r)
    d["active"] = bool(d["active"])
    return d


def list_rules(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute("SELECT * FROM wait_fee_rules ORDER BY id").fetchall()
    return [_row(r) for r in rows]


def get(conn: sqlite3.Connection, rule_id: int) -> dict | None:
    row = conn.execute("SELECT * FROM wait_fee_rules WHERE id=?", (rule_id,)).fetchone()
    return _row(row) if row else None


def get_active(conn: sqlite3.Connection) -> dict | None:
    row = conn.execute("SELECT * FROM wait_fee_rules WHERE active=1 ORDER BY id LIMIT 1").fetchone()
    return _row(row) if row else None


def insert(conn: sqlite3.Connection, label: str, free_min: float, per_min: float, active: bool) -> int:
    cur = conn.execute(
        "INSERT INTO wait_fee_rules(label,free_min,per_min,active,created_at) VALUES (?,?,?,?,datetime('now'))",
        (label, float(free_min), float(per_min), 1 if active else 0),
    )
    conn.commit()
    return int(cur.lastrowid)


def update(conn: sqlite3.Connection, rule_id: int, label: str, free_min: float, per_min: float, active: bool) -> None:
    conn.execute(
        "UPDATE wait_fee_rules SET label=?, free_min=?, per_min=?, active=? WHERE id=?",
        (label, float(free_min), float(per_min), 1 if active else 0, rule_id),
    )
    conn.commit()
