from pydantic import BaseModel, Field


class WaitRuleCreate(BaseModel):
    free_min: float = Field(0, ge=0, description="免费等候分钟，不得为负")
    per_min_price: float = Field(gt=0, description="超出后每分钟单价，必须为正")
    active: bool = True


class WaitRuleUpdate(BaseModel):
    free_min: float | None = Field(None, ge=0)
    per_min_price: float | None = Field(None, gt=0)
    active: bool | None = None
