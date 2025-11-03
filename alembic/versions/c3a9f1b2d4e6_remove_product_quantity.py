"""remove product.quantity and migrate values into inventory

Revision ID: c3a9f1b2d4e6
Revises: 9f47951cc979
Create Date: 2025-11-02 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3a9f1b2d4e6'
down_revision: Union[str, Sequence[str], None] = '9f47951cc979'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: migrate product.quantity -> inventory.quantity_in_stock, then drop column."""
    conn = op.get_bind()

    # 1) Create inventory rows for products that don't yet have inventory, copying quantity
    # Use a single INSERT ... SELECT that ignores conflicts (Postgres: ON CONFLICT DO NOTHING)
    conn.execute(
        sa.text(
            """
            INSERT INTO inventory (product_id, quantity_in_stock, reorder_level, created_at)
            SELECT p.id, p.quantity, 10, now()
            FROM products p
            WHERE NOT EXISTS (SELECT 1 FROM inventory i WHERE i.product_id = p.id)
            """
        )
    )

    # 2) For products that already have inventory rows, update inventory from product.quantity
    conn.execute(
        sa.text(
            """
            UPDATE inventory
            SET quantity_in_stock = p.quantity
            FROM products p
            WHERE inventory.product_id = p.id
            """
        )
    )

    # 3) Finally drop the column from products
    with op.batch_alter_table('products') as batch_op:
        batch_op.drop_column('quantity')


def downgrade() -> None:
    """Downgrade schema: re-add products.quantity and populate from inventory."""
    # 1) Recreate products.quantity with a sensible default
    with op.batch_alter_table('products') as batch_op:
        batch_op.add_column(sa.Column('quantity', sa.Integer(), nullable=False, server_default='0'))

    conn = op.get_bind()

    # 2) Populate products.quantity from inventory where present
    conn.execute(
        sa.text(
            """
            UPDATE products
            SET quantity = COALESCE((SELECT quantity_in_stock FROM inventory WHERE inventory.product_id = products.id), 0)
            """
        )
    )

    # 3) Remove server default so future inserts must set value explicitly if desired
    with op.batch_alter_table('products') as batch_op:
        batch_op.alter_column('quantity', server_default=None)
