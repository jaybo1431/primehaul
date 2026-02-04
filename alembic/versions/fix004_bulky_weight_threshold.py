"""add bulky_weight_threshold_kg to pricing_configs

Revision ID: fix004
Revises: fix003
Create Date: 2026-02-04

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision: str = 'fix004'
down_revision: Union[str, None] = 'fix003'
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

    if not column_exists(conn, 'pricing_configs', 'bulky_weight_threshold_kg'):
        op.add_column('pricing_configs', sa.Column('bulky_weight_threshold_kg', sa.Integer(), server_default='50'))


def downgrade() -> None:
    op.drop_column('pricing_configs', 'bulky_weight_threshold_kg')
