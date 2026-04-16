"""Add discount and refund columns to orders table

Revision ID: 002
Revises: 001
Create Date: 2026-03-28 00:01:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('orders', sa.Column('discount_amount', sa.Float(), nullable=False, server_default='0'))
    op.add_column('orders', sa.Column('discount_reason', sa.String(255), nullable=True))
    op.add_column('orders', sa.Column('refund_amount', sa.Float(), nullable=True))
    op.add_column('orders', sa.Column('refund_method', sa.String(20), nullable=True))
    op.add_column('orders', sa.Column('refund_reason', sa.Text(), nullable=True))
    op.add_column('orders', sa.Column('refunded_at', sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column('orders', 'refunded_at')
    op.drop_column('orders', 'refund_reason')
    op.drop_column('orders', 'refund_method')
    op.drop_column('orders', 'refund_amount')
    op.drop_column('orders', 'discount_reason')
    op.drop_column('orders', 'discount_amount')
