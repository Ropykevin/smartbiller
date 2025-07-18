"""Add notes field to RentLog

Revision ID: 8abb05709a73
Revises: 70f93032a68f
Create Date: 2025-07-12 22:50:53.512952

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8abb05709a73'
down_revision = '70f93032a68f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('rent_log', schema=None) as batch_op:
        batch_op.add_column(sa.Column('notes', sa.Text(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('rent_log', schema=None) as batch_op:
        batch_op.drop_column('notes')

    # ### end Alembic commands ###
