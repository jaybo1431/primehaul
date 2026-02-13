"""Add dropoff_property_type column to jobs

Revision ID: fix010
Revises: fix009
Create Date: 2026-02-13
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'fix010'
down_revision = 'fix009'
branch_labels = None
depends_on = None


def upgrade():
    # Add dropoff_property_type column to jobs table
    op.add_column('jobs', sa.Column('dropoff_property_type', sa.String(100), nullable=True))


def downgrade():
    op.drop_column('jobs', 'dropoff_property_type')
