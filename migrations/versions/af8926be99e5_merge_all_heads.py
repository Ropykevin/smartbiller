"""merge all heads

Revision ID: af8926be99e5
Revises: 0f4e9228f0bc, 1e557953ad73, 503a81ddaf06, f401b3c2d7e9
Create Date: 2025-07-12 22:13:23.729220

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'af8926be99e5'
down_revision = ('0f4e9228f0bc', '1e557953ad73', '503a81ddaf06', 'f401b3c2d7e9')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
