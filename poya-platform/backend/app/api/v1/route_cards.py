from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db.session import get_db
from ..services.route_card_service import RouteCardService
from ..schemas.route_card import RouteCard, RouteCardCreate, RouteCardUpdate
from ..core.security import get_current_active_user
from ..models.user import User

router = APIRouter()

@router.get("/production", response_model=List[RouteCard])
def get_production_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all active production orders."""
    return RouteCardService.get_production_orders(db)

@router.post("/route-cards", response_model=RouteCard)
def create_route_card(
    route_card_data: RouteCardCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new route card for a production order."""
    try:
        return RouteCardService.create_route_card(
            db=db,
            route_card_data=route_card_data,
            user_id=current_user.id
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/route-cards/{route_card_id}/confirm", response_model=RouteCard)
def confirm_route_card(
    route_card_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Confirm a route card and generate material preparation task."""
    try:
        return RouteCardService.confirm_route_card(
            db=db,
            route_card_id=route_card_id,
            user_id=current_user.id
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/route-cards/{route_card_id}", response_model=RouteCard)
def get_route_card(
    route_card_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a route card by ID."""
    route_card = RouteCardService.get_route_card(db, route_card_id)
    if not route_card:
        raise HTTPException(status_code=404, detail="Route card not found")
    return route_card
