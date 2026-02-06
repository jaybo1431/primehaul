"""Add final_quote_price to jobs

Revision ID: fix009
Revises: fix008
Create Date: 2026-02-06

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


revision = 'fix009'
down_revision = 'fix008'
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

    # Add final_quote_price column - the single fixed price set by boss when approving
    if not column_exists(conn, 'jobs', 'final_quote_price'):
        op.add_column('jobs', sa.Column('final_quote_price', sa.Integer(), nullable=True))


def downgrade():
    conn = op.get_bind()
    if column_exists(conn, 'jobs', 'final_quote_price'):
        op.drop_column('jobs', 'final_quote_price')
