"""Add deal fields to order_items

Revision ID: 003
Revises: 002
Create Date: 2026-04-07 00:01:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('order_items', sa.Column('is_deal_item', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('order_items', sa.Column('deal_selections', JSONB(), nullable=True))


def downgrade() -> None:
    op.drop_column('order_items', 'deal_selections')
    op.drop_column('order_items', 'is_deal_item')
