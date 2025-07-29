from fastapi import APIRouter
from . import users, tasks, orders, meetings, dashboard

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(meetings.router, prefix="/meetings", tags=["meetings"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
