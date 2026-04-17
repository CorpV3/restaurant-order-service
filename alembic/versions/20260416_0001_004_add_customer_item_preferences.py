"""Create customer_item_preferences table (idempotent)

Revision ID: 004
Revises: 003
Create Date: 2026-04-16

In environments bootstrapped via SQLAlchemy create_all(), migration 001 was
skipped (stamped) because its columns already existed. That means the
customer_item_preferences table was never created. This migration adds it
safely using IF NOT EXISTS so it's harmless in environments where it does exist.
"""
from alembic import op

revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        CREATE TABLE IF NOT EXISTS customer_item_preferences (
            id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            customer_identifier VARCHAR(255) NOT NULL,
            restaurant_id   UUID NOT NULL,
            menu_item_id    UUID NOT NULL,
            order_count     INTEGER NOT NULL DEFAULT 0,
            total_quantity  INTEGER NOT NULL DEFAULT 0,
            total_spent     FLOAT   NOT NULL DEFAULT 0.0,
            recency_score   FLOAT   NOT NULL DEFAULT 0.0,
            frequency_score FLOAT   NOT NULL DEFAULT 0.0,
            monetary_score  FLOAT   NOT NULL DEFAULT 0.0,
            first_ordered_at TIMESTAMP,
            last_ordered_at  TIMESTAMP,
            created_at      TIMESTAMP NOT NULL DEFAULT now(),
            updated_at      TIMESTAMP NOT NULL DEFAULT now()
        )
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_customer_restaurant
        ON customer_item_preferences(customer_identifier, restaurant_id)
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_customer_menu_item
        ON customer_item_preferences(customer_identifier, menu_item_id)
    """)


def downgrade():
    op.execute("DROP INDEX IF EXISTS idx_customer_menu_item")
    op.execute("DROP INDEX IF EXISTS idx_customer_restaurant")
    op.execute("DROP TABLE IF EXISTS customer_item_preferences")
