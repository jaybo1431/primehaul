"""Add learned_corrections table for self-learning ML

Revision ID: fix007_learned_corrections
Revises: fix006_partner_accounts
Create Date: 2026-02-05
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'fix007'
down_revision = 'fix006'
branch_labels = None
depends_on = None


def upgrade():
    # Create learned_corrections table
    op.create_table(
        'learned_corrections',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('ai_pattern', sa.String(255), nullable=False, index=True),
        sa.Column('corrected_name', sa.String(255), nullable=False),
        sa.Column('corrected_category', sa.String(100)),
        sa.Column('learned_length_cm', sa.Numeric(10, 2)),
        sa.Column('learned_width_cm', sa.Numeric(10, 2)),
        sa.Column('learned_height_cm', sa.Numeric(10, 2)),
        sa.Column('learned_weight_kg', sa.Numeric(10, 2)),
        sa.Column('learned_cbm', sa.Numeric(10, 4)),
        sa.Column('times_seen', sa.Integer, default=0),
        sa.Column('times_corrected', sa.Integer, default=0),
        sa.Column('confidence', sa.Numeric(3, 2), default=0),
        sa.Column('auto_apply', sa.Boolean, default=False),
        sa.Column('last_seen_at', sa.DateTime(timezone=True)),
        sa.Column('last_learned_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Create index
    op.create_index('idx_learned_ai_pattern', 'learned_corrections', ['ai_pattern'])


def downgrade():
    op.drop_index('idx_learned_ai_pattern')
    op.drop_table('learned_corrections')
