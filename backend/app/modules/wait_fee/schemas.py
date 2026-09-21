from pydantic import BaseModel, Field


class WaitRuleCreate(BaseModel):
    label: str = Field(default="等候规则", min_length=1)
    free_min: float = Field(ge=0)
    per_min: float = Field(gt=0)
    active: bool = True


class WaitRuleUpdate(BaseModel):
    label: str | None = Field(default=None, min_length=1)
    free_min: float | None = Field(default=None, ge=0)
    per_min: float | None = Field(default=None, gt=0)
    active: bool | None = None
