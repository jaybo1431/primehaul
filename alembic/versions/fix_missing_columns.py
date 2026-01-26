"""fix_missing_columns

Revision ID: fix001
Revises: 1c9ab1b72be0
Create Date: 2026-01-26

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = 'fix001'
down_revision: Union[str, None] = '1c9ab1b72be0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def column_exists(conn, table, column):
    result = conn.execute(text(f"""
        SELECT column_name FROM information_schema.columns
        WHERE table_name='{table}' AND column_name='{column}'
    """))
    return result.fetchone() is not None


def upgrade() -> None:
    conn = op.get_bind()

    # Jobs table - all potentially missing columns
    if not column_exists(conn, 'jobs', 'customer_provides_packing'):
        op.add_column('jobs', sa.Column('customer_provides_packing', sa.Boolean(), nullable=True, server_default='false'))

    if not column_exists(conn, 'jobs', 'packing_service_rooms'):
        op.add_column('jobs', sa.Column('packing_service_rooms', JSONB, nullable=True))

    if not column_exists(conn, 'jobs', 'packing_labor_hours'):
        op.add_column('jobs', sa.Column('packing_labor_hours', sa.Float(), nullable=True))

    if not column_exists(conn, 'jobs', 'packing_labor_cost'):
        op.add_column('jobs', sa.Column('packing_labor_cost', sa.Float(), nullable=True))

    # Pricing configs table
    if not column_exists(conn, 'pricing_configs', 'packing_labor_per_hour'):
        op.add_column('pricing_configs', sa.Column('packing_labor_per_hour', sa.DECIMAL(10, 2), nullable=False, server_default='40.00'))


def downgrade() -> None:
    pass  # Don't remove columns on downgrade
