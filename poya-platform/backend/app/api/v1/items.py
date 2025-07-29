from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional

from ..core.security import get_current_user
from ..models.user import User
from ..models.item import Item
from ..models.item_category import ItemCategory
from ..schemas.item import ItemResponse, ItemCreate
from ..schemas.item_category import ItemCategoryTree, ItemCategoryCreate
from ..db.session import get_db

router = APIRouter()

@router.get("/categories", response_model=List[ItemCategoryTree])
async def get_item_categories(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)
):
    """Get all item categories in a tree structure"""
    # Get root categories (those without parent)
    root_categories = db.query(ItemCategory).filter(
        ItemCategory.parent_id.is_(None)
    ).all()
    
    return [category.to_tree_dict() for category in root_categories]

@router.get("", response_model=List[ItemResponse])
async def get_items(
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)
):
    """
    Get all items with optional filtering
    - search: Search in item_code, name, and description
    - category_id: Filter by category
    """
    query = db.query(Item)
    
    # Apply category filter
    if category_id is not None:
        query = query.filter(Item.category_id == category_id)
    
    # Apply search filter
    if search:
        search_filter = or_(
            Item.item_code.ilike(f"%{search}%"),
            Item.name.ilike(f"%{search}%"),
            Item.description.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    # Apply pagination
    items = query.offset(skip).limit(limit).all()
    
    # Enhance items with category name
    response_items = []
    for item in items:
        item_dict = ItemResponse.from_orm(item).dict()
        item_dict["category_name"] = item.category.name
        response_items.append(ItemResponse(**item_dict))
    
    return response_items

@router.post("/categories", response_model=ItemCategoryTree)
async def create_category(
    category_data: ItemCategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new item category"""
    # Verify parent exists if provided
    if category_data.parent_id:
        parent = db.query(ItemCategory).filter(ItemCategory.id == category_data.parent_id).first()
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent category not found"
            )
    
    # Create category
    db_category = ItemCategory(
        name=category_data.name,
        description=category_data.description,
        parent_id=category_data.parent_id
    )
    
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    
    return db_category.to_tree_dict()

@router.post("", response_model=ItemResponse)
async def create_item(
    item_data: ItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new item"""
    # Verify category exists
    category = db.query(ItemCategory).filter(ItemCategory.id == item_data.category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category not found"
        )
    
    # Check if item_code is unique
    if db.query(Item).filter(Item.item_code == item_data.item_code).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Item code already exists"
        )
    
    # Create item
    db_item = Item(
        item_code=item_data.item_code,
        name=item_data.name,
        description=item_data.description,
        category_id=item_data.category_id
    )
    
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    
    # Add category name to response
    response = ItemResponse.from_orm(db_item).dict()
    response["category_name"] = category.name
    
    return ItemResponse(**response)
