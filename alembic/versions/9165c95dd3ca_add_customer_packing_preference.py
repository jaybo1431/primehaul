"""add_customer_packing_preference

Revision ID: 9165c95dd3ca
Revises: 0c1c31e6b50f
Create Date: 2026-01-13 17:46:47.616889

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9165c95dd3ca'
down_revision: Union[str, None] = '0c1c31e6b50f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add customer_provides_packing column to jobs table
    op.add_column('jobs', sa.Column('customer_provides_packing', sa.Boolean(), nullable=True, server_default='false'))


def downgrade() -> None:
    # Remove customer_provides_packing column from jobs table
    op.drop_column('jobs', 'customer_provides_packing')
