"""Add performance indexes for dashboard queries

Revision ID: fix015
Revises: fix014
Create Date: 2026-02-24
"""
from alembic import op
from sqlalchemy import text

revision = 'fix015'
down_revision = 'fix014'
branch_labels = None
depends_on = None


def index_exists(conn, index_name):
    result = conn.execute(text(f"""
        SELECT 1 FROM pg_indexes WHERE indexname = '{index_name}'
    """))
    return result.fetchone() is not None


def upgrade():
    conn = op.get_bind()

    if not index_exists(conn, 'idx_jobs_created_at'):
        op.create_index('idx_jobs_created_at', 'jobs', ['created_at'])

    if not index_exists(conn, 'idx_jobs_status_submitted'):
        op.create_index('idx_jobs_status_submitted', 'jobs', ['status', 'submitted_at'])

    if not index_exists(conn, 'idx_item_feedback_created'):
        op.create_index('idx_item_feedback_created', 'item_feedback', ['created_at'])


def downgrade():
    conn = op.get_bind()
    for idx in ['idx_jobs_created_at', 'idx_jobs_status_submitted', 'idx_item_feedback_created']:
        if index_exists(conn, idx):
            op.drop_index(idx)
