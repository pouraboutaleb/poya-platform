"""add_production_reports

Revision ID: 004_add_production_reports
Revises: 003_add_item_master
Create Date: 2025-07-29

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = '004_add_production_reports'
down_revision = '003_add_item_master'
branch_labels = None
depends_on = None

def upgrade():
    # Create production_reports table
    op.create_table(
        'production_reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('report_date', sa.Date(), nullable=False),
        sa.Column('shift', sa.Enum('morning', 'afternoon', 'night', name='shiftenum'), nullable=False),
        sa.Column('daily_challenge', sa.Text(), nullable=True),
        sa.Column('solutions_implemented', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('report_date', 'shift', name='uix_report_date_shift')
    )
    op.create_index(op.f('ix_production_reports_id'), 'production_reports', ['id'], unique=False)
    
    # Create production_logs table
    op.create_table(
        'production_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('quantity_produced', sa.Float(), nullable=False),
        sa.Column('target_quantity', sa.Float(), nullable=False),
        sa.Column('efficiency', sa.Float(), nullable=True),
        sa.Column('remarks', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('report_id', sa.Integer(), nullable=False),
        sa.Column('item_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['item_id'], ['items.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['report_id'], ['production_reports.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_production_logs_id'), 'production_logs', ['id'], unique=False)
    
    # Create stoppages table
    op.create_table(
        'stoppages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('type', sa.Enum(
            'maintenance',
            'breakdown',
            'material_shortage',
            'setup_changeover',
            'quality_issue',
            'other',
            name='stoppagetype'
        ), nullable=False),
        sa.Column('reason', sa.String(), nullable=False),
        sa.Column('duration', sa.Float(), nullable=False),
        sa.Column('action_taken', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('report_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['report_id'], ['production_reports.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_stoppages_id'), 'stoppages', ['id'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_stoppages_id'), table_name='stoppages')
    op.drop_table('stoppages')
    op.drop_index(op.f('ix_production_logs_id'), table_name='production_logs')
    op.drop_table('production_logs')
    op.drop_index(op.f('ix_production_reports_id'), table_name='production_reports')
    op.drop_table('production_reports')
    op.execute('DROP TYPE shiftenum')
    op.execute('DROP TYPE stoppagetype')
