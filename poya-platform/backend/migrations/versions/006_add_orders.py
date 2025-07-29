"""Add orders table

Revision ID: 006_add_orders
Revises: 005_add_warehouse_requests
Create Date: 2025-07-29 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '006_add_orders'
down_revision = '005_add_warehouse_requests'
branch_labels = None
depends_on = None

def upgrade():
    # Create orders table
    op.create_table(
        'orders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_type', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('priority', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('required_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by_id', sa.Integer(), nullable=False),
        sa.Column('item_id', sa.Integer(), nullable=False),
        sa.Column('warehouse_request_item_id', sa.Integer(), nullable=True),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('remarks', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['item_id'], ['items.id'], ),
        sa.ForeignKeyConstraint(['warehouse_request_item_id'], ['warehouse_request_items.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_orders_id'), 'orders', ['id'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_orders_id'), table_name='orders')
    op.drop_table('orders')
