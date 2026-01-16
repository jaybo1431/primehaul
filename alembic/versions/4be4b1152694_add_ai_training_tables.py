"""add_ai_training_tables

Revision ID: 4be4b1152694
Revises: cac20d85e9b9
Create Date: 2026-01-13 22:12:42.863737

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB


# revision identifiers, used by Alembic.
revision: str = '4be4b1152694'
down_revision: Union[str, None] = 'cac20d85e9b9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create furniture_catalog table
    op.create_table(
        'furniture_catalog',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('source', sa.String(50), nullable=False),
        sa.Column('product_id', sa.String(100)),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('category', sa.String(100)),
        sa.Column('length_cm', sa.Numeric(10, 2)),
        sa.Column('width_cm', sa.Numeric(10, 2)),
        sa.Column('height_cm', sa.Numeric(10, 2)),
        sa.Column('cbm', sa.Numeric(10, 4)),
        sa.Column('weight_kg', sa.Numeric(10, 2)),
        sa.Column('is_bulky', sa.Boolean, default=False),
        sa.Column('is_fragile', sa.Boolean, default=False),
        sa.Column('packing_requirement', sa.String(50)),
        sa.Column('image_urls', JSONB),
        sa.Column('description', sa.Text),
        sa.Column('material', sa.String(100)),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    )

    # Create item_feedback table
    op.create_table(
        'item_feedback',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('item_id', UUID(as_uuid=True), sa.ForeignKey('items.id', ondelete='CASCADE'), nullable=False),
        sa.Column('company_id', UUID(as_uuid=True), sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL')),
        sa.Column('ai_detected_name', sa.String(255)),
        sa.Column('ai_detected_category', sa.String(100)),
        sa.Column('ai_confidence', sa.Numeric(3, 2)),
        sa.Column('corrected_name', sa.String(255)),
        sa.Column('corrected_category', sa.String(100)),
        sa.Column('corrected_dimensions', JSONB),
        sa.Column('corrected_cbm', sa.Numeric(10, 4)),
        sa.Column('corrected_weight', sa.Numeric(10, 2)),
        sa.Column('feedback_type', sa.String(50)),
        sa.Column('notes', sa.Text),
        sa.Column('catalog_item_id', UUID(as_uuid=True), sa.ForeignKey('furniture_catalog.id', ondelete='SET NULL')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    )

    # Create training_dataset table
    op.create_table(
        'training_dataset',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('image_url', sa.String(500)),
        sa.Column('image_hash', sa.String(64)),
        sa.Column('item_name', sa.String(255), nullable=False),
        sa.Column('item_category', sa.String(100), nullable=False),
        sa.Column('length_cm', sa.Numeric(10, 2)),
        sa.Column('width_cm', sa.Numeric(10, 2)),
        sa.Column('height_cm', sa.Numeric(10, 2)),
        sa.Column('cbm', sa.Numeric(10, 4)),
        sa.Column('weight_kg', sa.Numeric(10, 2)),
        sa.Column('is_bulky', sa.Boolean),
        sa.Column('is_fragile', sa.Boolean),
        sa.Column('packing_requirement', sa.String(50)),
        sa.Column('source_type', sa.String(50)),
        sa.Column('source_id', UUID(as_uuid=True)),
        sa.Column('confidence_score', sa.Numeric(3, 2)),
        sa.Column('verified', sa.Boolean, default=False),
        sa.Column('used_in_training', sa.Boolean, default=False),
        sa.Column('training_batch', sa.String(50)),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    )


def downgrade() -> None:
    op.drop_table('training_dataset')
    op.drop_table('item_feedback')
    op.drop_table('furniture_catalog')
