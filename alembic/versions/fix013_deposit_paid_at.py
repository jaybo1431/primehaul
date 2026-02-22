"""Add deposit_paid_at column to jobs

Revision ID: fix013
Revises: fix012
Create Date: 2026-02-22
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

revision = 'fix013'
down_revision = 'fix012'
branch_labels = None
depends_on = None


def column_exists(conn, table, column):
    result = conn.execute(text(f"""
        SELECT column_name FROM information_schema.columns
        WHERE table_name='{table}' AND column_name='{column}'
    """))
    return result.fetchone() is not None


def upgrade():
    conn = op.get_bind()
    if not column_exists(conn, 'jobs', 'deposit_paid_at'):
        op.add_column('jobs', sa.Column('deposit_paid_at', sa.DateTime(timezone=True)))


def downgrade():
    conn = op.get_bind()
    if column_exists(conn, 'jobs', 'deposit_paid_at'):
        op.drop_column('jobs', 'deposit_paid_at')
