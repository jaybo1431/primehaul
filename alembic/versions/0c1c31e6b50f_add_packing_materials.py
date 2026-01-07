"""add_packing_materials

Revision ID: 0c1c31e6b50f
Revises: 7ad4ef51f586
Create Date: 2026-01-04 15:17:49.977620

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0c1c31e6b50f'
down_revision: Union[str, None] = '7ad4ef51f586'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add packing classification to items table
    op.add_column('items', sa.Column('item_category', sa.String(50), nullable=True))
    op.add_column('items', sa.Column('packing_requirement', sa.String(50), nullable=True))

    # Add packing materials pricing to pricing_configs table
    op.add_column('pricing_configs', sa.Column('pack1_price', sa.DECIMAL(10, 2), nullable=False, server_default='1.05'))
    op.add_column('pricing_configs', sa.Column('pack2_price', sa.DECIMAL(10, 2), nullable=False, server_default='1.55'))
    op.add_column('pricing_configs', sa.Column('pack3_price', sa.DECIMAL(10, 2), nullable=False, server_default='2.00'))
    op.add_column('pricing_configs', sa.Column('pack6_price', sa.DECIMAL(10, 2), nullable=False, server_default='1.05'))
    op.add_column('pricing_configs', sa.Column('robe_carton_price', sa.DECIMAL(10, 2), nullable=False, server_default='10.00'))
    op.add_column('pricing_configs', sa.Column('tape_price', sa.DECIMAL(10, 2), nullable=False, server_default='1.14'))
    op.add_column('pricing_configs', sa.Column('paper_price', sa.DECIMAL(10, 2), nullable=False, server_default='7.50'))
    op.add_column('pricing_configs', sa.Column('mattress_cover_price', sa.DECIMAL(10, 2), nullable=False, server_default='1.74'))


def downgrade() -> None:
    # Remove pricing_configs columns
    op.drop_column('pricing_configs', 'mattress_cover_price')
    op.drop_column('pricing_configs', 'paper_price')
    op.drop_column('pricing_configs', 'tape_price')
    op.drop_column('pricing_configs', 'robe_carton_price')
    op.drop_column('pricing_configs', 'pack6_price')
    op.drop_column('pricing_configs', 'pack3_price')
    op.drop_column('pricing_configs', 'pack2_price')
    op.drop_column('pricing_configs', 'pack1_price')

    # Remove items columns
    op.drop_column('items', 'packing_requirement')
    op.drop_column('items', 'item_category')
