from pydantic import BaseModel, Field
from typing import Optional, List

class ItemCategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    parent_id: Optional[int] = None

class ItemCategoryCreate(ItemCategoryBase):
    pass

class ItemCategoryResponse(ItemCategoryBase):
    id: int
    children: List['ItemCategoryResponse'] = []

    class Config:
        orm_mode = True

# This is needed for the recursive nature of ItemCategoryResponse
ItemCategoryResponse.model_rebuild()

class ItemCategoryTree(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    children: List['ItemCategoryTree'] = []

    class Config:
        orm_mode = True

# This is needed for the recursive nature of ItemCategoryTree
ItemCategoryTree.model_rebuild()
