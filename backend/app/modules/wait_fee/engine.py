"""等候费计价引擎：计入分钟 = max(0, 等候分钟 - 免费分钟)。"""


def calc_wait_fee(wait_min, rule):
    """按规则计算等候费。无启用规则（或已全部停用）时等候费为 0。

    计入分钟 = max(0, 等候分钟 - 免费分钟)，等候费 = 计入分钟 * 单价。
    返回规则标识、免费分钟、计入分钟与等候费。
    """
    if not rule:
        return {"wait_rule_id": None, "free_min": 0, "charged_min": 0, "wait_fee": 0.0}
    free = float(rule["free_min"])
    price = float(rule["per_min_price"])
    charged = max(0.0, float(wait_min) - free)
    return {
        "wait_rule_id": rule["id"],
        "free_min": free,
        "charged_min": round(charged, 1),
        "wait_fee": round(charged * price, 2),
    }
