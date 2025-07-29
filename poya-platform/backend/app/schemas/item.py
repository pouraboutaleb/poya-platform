from pydantic import BaseModel, Field
from typing import Optional

class ItemBase(BaseModel):
    item_code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    category_id: int

class ItemCreate(ItemBase):
    pass

class ItemResponse(ItemBase):
    id: int
    category_name: Optional[str] = None

    class Config:
        orm_mode = True
