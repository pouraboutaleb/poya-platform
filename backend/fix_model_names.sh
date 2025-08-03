#!/bin/bash

# Update foreign key references
find . -type f -name "*.py" -exec sed -i 's/ForeignKey("users\.id/ForeignKey("user.id/g' {} +
find . -type f -name "*.py" -exec sed -i 's/ForeignKey("roles\.id/ForeignKey("role.id/g' {} +
find . -type f -name "*.py" -exec sed -i 's/ForeignKey("items\.id/ForeignKey("item.id/g' {} +
find . -type f -name "*.py" -exec sed -i 's/ForeignKey("tasks\.id/ForeignKey("task.id/g' {} +
find . -type f -name "*.py" -exec sed -i 's/ForeignKey("meetings\.id/ForeignKey("meeting.id/g' {} +
find . -type f -name "*.py" -exec sed -i 's/ForeignKey("orders\.id/ForeignKey("order.id/g' {} +
find . -type f -name "*.py" -exec sed -i 's/ForeignKey("warehouse_requests\.id/ForeignKey("warehouse_request.id/g' {} +
find . -type f -name "*.py" -exec sed -i 's/ForeignKey("warehouse_request_items\.id/ForeignKey("warehouse_request_item.id/g' {} +
find . -type f -name "*.py" -exec sed -i 's/ForeignKey("production_reports\.id/ForeignKey("production_report.id/g' {} +
find . -type f -name "*.py" -exec sed -i 's/ForeignKey("route_cards\.id/ForeignKey("route_card.id/g' {} +
find . -type f -name "*.py" -exec sed -i 's/ForeignKey("change_request_approvals\.id/ForeignKey("change_request_approval.id/g' {} +

# Update table names
find . -type f -name "*.py" -exec sed -i 's/__tablename__ = "users"/__tablename__ = "user"/g' {} +
find . -type f -name "*.py" -exec sed -i 's/__tablename__ = "roles"/__tablename__ = "role"/g' {} +
find . -type f -name "*.py" -exec sed -i 's/__tablename__ = "items"/__tablename__ = "item"/g' {} +
find . -type f -name "*.py" -exec sed -i 's/__tablename__ = "tasks"/__tablename__ = "task"/g' {} +
find . -type f -name "*.py" -exec sed -i 's/__tablename__ = "meetings"/__tablename__ = "meeting"/g' {} +
find . -type f -name "*.py" -exec sed -i 's/__tablename__ = "orders"/__tablename__ = "order"/g' {} +
find . -type f -name "*.py" -exec sed -i 's/__tablename__ = "route_cards"/__tablename__ = "route_card"/g' {} +
find . -type f -name "*.py" -exec sed -i 's/__tablename__ = "audit_logs"/__tablename__ = "audit_log"/g' {} +
find . -type f -name "*.py" -exec sed -i 's/__tablename__ = "production_logs"/__tablename__ = "production_log"/g' {} +
find . -type f -name "*.py" -exec sed -i 's/__tablename__ = "stoppages"/__tablename__ = "stoppage"/g' {} +
find . -type f -name "*.py" -exec sed -i 's/__tablename__ = "notifications"/__tablename__ = "notification"/g' {} +
find . -type f -name "*.py" -exec sed -i 's/__tablename__ = "change_request_approvals"/__tablename__ = "change_request_approval"/g' {} +
find . -type f -name "*.py" -exec sed -i 's/__tablename__ = "general_submissions"/__tablename__ = "general_submission"/g' {} +
