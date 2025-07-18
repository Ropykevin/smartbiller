"""Initial migration

Revision ID: 7b431c28b473
Revises: 
Create Date: 2025-06-20 11:26:37.266650

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7b431c28b473'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('landlord',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('password', sa.String(length=200), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('property',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('location', sa.String(length=200), nullable=False),
    sa.Column('payment_method', sa.String(length=50), nullable=False),
    sa.Column('payment_destination', sa.String(length=100), nullable=False),
    sa.Column('landlord_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['landlord_id'], ['landlord.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('unit',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('unit_number', sa.String(length=20), nullable=False),
    sa.Column('rent_amount', sa.Float(), nullable=False),
    sa.Column('property_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['property_id'], ['property.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tenant',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('phone', sa.String(length=20), nullable=False),
    sa.Column('unit_id', sa.Integer(), nullable=False),
    sa.Column('login_code', sa.String(length=10), nullable=True),
    sa.Column('login_code_expiry', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['unit_id'], ['unit.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('unit_id')
    )
    op.create_table('rent_log',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('tenant_id', sa.Integer(), nullable=False),
    sa.Column('amount_paid', sa.Float(), nullable=False),
    sa.Column('date_paid', sa.Date(), nullable=False),
    sa.Column('month_paid_for', sa.String(length=20), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.Column('receipt_number', sa.String(length=50), nullable=True),
    sa.ForeignKeyConstraint(['tenant_id'], ['tenant.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('rent_log')
    op.drop_table('tenant')
    op.drop_table('unit')
    op.drop_table('property')
    op.drop_table('landlord')
    # ### end Alembic commands ###
