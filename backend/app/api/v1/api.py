from fastapi import APIRouter

from . import users, auth, tasks, items, production_reports, warehouse_requests, orders, material_delivery, production_followup, part_pickup, qc_inspection, change_addendum, submissions, meetings, notifications, static_files

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(production_reports.router, prefix="/production-reports", tags=["production-reports"])
api_router.include_router(warehouse_requests.router, prefix="/warehouse", tags=["warehouse"])
api_router.include_router(orders.router, prefix="/warehouse-requests", tags=["orders"])
api_router.include_router(material_delivery.router, prefix="/material-delivery", tags=["material-delivery"])
api_router.include_router(production_followup.router, prefix="/production-followup", tags=["production-followup"])
api_router.include_router(part_pickup.router, prefix="/part-pickup", tags=["part-pickup"])
api_router.include_router(qc_inspection.router, prefix="/qc", tags=["qc-inspection"])
api_router.include_router(change_addendum.router, prefix="/warehouse-requests", tags=["change-addendum"])
api_router.include_router(submissions.router, prefix="/api/v1", tags=["submissions"])
api_router.include_router(meetings.router, prefix="/api/v1", tags=["meetings"])
api_router.include_router(static_files.router, tags=["static-files"])
