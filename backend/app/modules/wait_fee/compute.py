"""等候费纯计算：不依赖数据库，供计价引擎与测试直接复用。"""


def wait_charge(wait_min: float, rule: dict | None) -> tuple[float, float]:
    """返回 (计入分钟, 等候费)。

    计入分钟 = 等候分钟 - 免费分钟，与零取大；无启用规则时两者均为零。
    等候分钟为负属非法输入，抛 ValueError（整单拒绝）。
    """
    wait = float(wait_min or 0.0)
    if wait < 0:
        raise ValueError("等候分钟不能为负")
    if not rule:
        return 0.0, 0.0
    billable = max(0.0, wait - float(rule["free_min"]))
    fee = round(billable * float(rule["per_min"]), 2)
    return round(billable, 2), fee
