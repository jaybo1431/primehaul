"""add_packing_service_fields

Revision ID: cac20d85e9b9
Revises: 9165c95dd3ca
Create Date: 2026-01-13 17:52:41.302700

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = 'cac20d85e9b9'
down_revision: Union[str, None] = '9165c95dd3ca'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add packing_service_rooms to jobs table (JSONB for list of room IDs)
    op.add_column('jobs', sa.Column('packing_service_rooms', JSONB, nullable=True))

    # Add packing_labor_per_hour to pricing_configs table
    op.add_column('pricing_configs', sa.Column('packing_labor_per_hour', sa.DECIMAL(10, 2), nullable=False, server_default='40.00'))


def downgrade() -> None:
    # Remove packing_labor_per_hour from pricing_configs
    op.drop_column('pricing_configs', 'packing_labor_per_hour')

    # Remove packing_service_rooms from jobs
    op.drop_column('jobs', 'packing_service_rooms')
