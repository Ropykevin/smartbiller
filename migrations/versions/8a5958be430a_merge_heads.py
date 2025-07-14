"""Merge heads

Revision ID: 8a5958be430a
Revises: 8abb05709a73, add_admin_tables
Create Date: 2025-07-13 20:07:32.291377

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8a5958be430a'
down_revision = ('8abb05709a73', 'add_admin_tables')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
