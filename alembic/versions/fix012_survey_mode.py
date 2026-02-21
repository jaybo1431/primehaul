"""Add survey_mode column to jobs

Revision ID: fix012
Revises: fix011
Create Date: 2026-02-17
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

revision = 'fix012'
down_revision = 'fix011'
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
    if not column_exists(conn, 'jobs', 'survey_mode'):
        op.add_column('jobs', sa.Column('survey_mode', sa.String(20), nullable=False, server_default='quote'))


def downgrade():
    conn = op.get_bind()
    if column_exists(conn, 'jobs', 'survey_mode'):
        op.drop_column('jobs', 'survey_mode')
