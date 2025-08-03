"""
Import all models here to ensure proper table creation order.
This file should be imported when creating tables or running migrations.
"""

from app.db.base_class import Base  # noqa
from app.models.user import User, Role  # noqa
from app.models.item_category import ItemCategory  # noqa
from app.models.item import Item  # noqa
from app.models.warehouse_request import WarehouseRequest, WarehouseRequestItem  # noqa
from app.models.order import Order  # noqa
from app.models.task import Task  # noqa
from app.models.route_card import RouteCard  # noqa
from app.models.production_report import ProductionReport  # noqa
from app.models.production_log import ProductionLog  # noqa
from app.models.stoppage import Stoppage  # noqa
from app.models.meeting import Meeting, MeetingAgendaItem, MeetingMinutes  # noqa
from app.models.audit import AuditLog  # noqa
from app.models.notification import Notification  # noqa
from app.models.chat import ChatMessage  # noqa
from app.models.change_request_approval import ChangeRequestApproval  # noqa
from app.models.general_submission import GeneralSubmission  # noqa
