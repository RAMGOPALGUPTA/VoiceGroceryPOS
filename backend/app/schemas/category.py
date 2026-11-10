from pydantic import BaseModel, ConfigDict, Field


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    parent_id: int | None = Field(default=None, gt=0)


class CategoryRead(BaseModel):
    id: int
    name: str
    parent_id: int | None
    model_config = ConfigDict(from_attributes=True)
