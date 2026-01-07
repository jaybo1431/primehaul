"""add_access_parameters

Revision ID: 7ad4ef51f586
Revises: 72e5e19b186d
Create Date: 2026-01-04 14:47:36.317373

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '7ad4ef51f586'
down_revision: Union[str, None] = '72e5e19b186d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add access parameter columns to jobs table
    op.add_column('jobs', sa.Column('pickup_access', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('jobs', sa.Column('dropoff_access', postgresql.JSONB(astext_type=sa.Text()), nullable=True))

    # Add access pricing columns to pricing_configs table
    op.add_column('pricing_configs', sa.Column('price_per_floor', sa.DECIMAL(precision=10, scale=2), nullable=False, server_default='15.00'))
    op.add_column('pricing_configs', sa.Column('no_lift_surcharge', sa.DECIMAL(precision=10, scale=2), nullable=False, server_default='50.00'))
    op.add_column('pricing_configs', sa.Column('parking_street_fee', sa.DECIMAL(precision=10, scale=2), nullable=False, server_default='25.00'))
    op.add_column('pricing_configs', sa.Column('parking_permit_fee', sa.DECIMAL(precision=10, scale=2), nullable=False, server_default='40.00'))
    op.add_column('pricing_configs', sa.Column('parking_limited_fee', sa.DECIMAL(precision=10, scale=2), nullable=False, server_default='60.00'))
    op.add_column('pricing_configs', sa.Column('parking_distance_per_50m', sa.DECIMAL(precision=10, scale=2), nullable=False, server_default='10.00'))
    op.add_column('pricing_configs', sa.Column('narrow_access_fee', sa.DECIMAL(precision=10, scale=2), nullable=False, server_default='35.00'))
    op.add_column('pricing_configs', sa.Column('time_restriction_fee', sa.DECIMAL(precision=10, scale=2), nullable=False, server_default='25.00'))
    op.add_column('pricing_configs', sa.Column('booking_required_fee', sa.DECIMAL(precision=10, scale=2), nullable=False, server_default='20.00'))
    op.add_column('pricing_configs', sa.Column('outdoor_steps_per_5', sa.DECIMAL(precision=10, scale=2), nullable=False, server_default='15.00'))
    op.add_column('pricing_configs', sa.Column('outdoor_path_fee', sa.DECIMAL(precision=10, scale=2), nullable=False, server_default='20.00'))


def downgrade() -> None:
    # Remove pricing config columns
    op.drop_column('pricing_configs', 'outdoor_path_fee')
    op.drop_column('pricing_configs', 'outdoor_steps_per_5')
    op.drop_column('pricing_configs', 'booking_required_fee')
    op.drop_column('pricing_configs', 'time_restriction_fee')
    op.drop_column('pricing_configs', 'narrow_access_fee')
    op.drop_column('pricing_configs', 'parking_distance_per_50m')
    op.drop_column('pricing_configs', 'parking_limited_fee')
    op.drop_column('pricing_configs', 'parking_permit_fee')
    op.drop_column('pricing_configs', 'parking_street_fee')
    op.drop_column('pricing_configs', 'no_lift_surcharge')
    op.drop_column('pricing_configs', 'price_per_floor')

    # Remove job access columns
    op.drop_column('jobs', 'dropoff_access')
    op.drop_column('jobs', 'pickup_access')
