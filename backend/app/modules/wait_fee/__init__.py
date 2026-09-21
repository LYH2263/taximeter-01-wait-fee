"""等候费模块：免费等候分钟 + 超出后每分钟单价。

- engine:     纯计价逻辑（计入分钟 = max(0, 等候 - 免费)）
- repository: 规则落库与「同一时刻仅一条启用规则」约束
- schemas:    入参校验（免费分钟 >= 0，单价 > 0）
- router:     列表 / 创建 / 更新 / 停用
"""
from app.modules.wait_fee.engine import calc_wait_fee
from app.modules.wait_fee.repository import WaitRuleConflict

__all__ = ["calc_wait_fee", "WaitRuleConflict"]
