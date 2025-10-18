"""merge users and customers tables with RBAC

Revision ID: 5c2c72f3d2a4
Revises: 9f47951cc979
Create Date: 2025-10-16 10:30:01.718785

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '5c2c72f3d2a4'
down_revision: Union[str, Sequence[str], None] = '9f47951cc979'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Merge customers into users table with RBAC."""

    # Step 0: Create the UserRole enum type
    user_role_enum = postgresql.ENUM('CUSTOMER', 'ADMIN', 'SUPERADMIN', name='userrole')
    user_role_enum.create(op.get_bind(), checkfirst=True)

    # Step 1: Add new columns to users table (nullable first to allow data migration)
    op.add_column('users', sa.Column('username', sa.String(), nullable=True))
    op.add_column('users', sa.Column('password_hash', sa.String(), nullable=True))
    op.add_column('users', sa.Column('full_name', sa.String(), nullable=True))
    op.add_column('users', sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False))
    op.add_column('users', sa.Column('role', sa.Enum('CUSTOMER', 'ADMIN', 'SUPERADMIN', name='userrole'), server_default='CUSTOMER', nullable=False))
    op.add_column('users', sa.Column('is_superadmin', sa.Boolean(), server_default='false', nullable=False))
    op.add_column('users', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))

    # Step 2: Make 'name' column nullable (it was required before)
    op.alter_column('users', 'name', existing_type=sa.VARCHAR(), nullable=True)

    # Step 3: Migrate data from customers table to users table
    # Insert all customers into users table with their data
    op.execute("""
        INSERT INTO users (username, password_hash, email, full_name, is_active, role, is_superadmin, created_at, updated_at)
        SELECT username, password_hash, email, full_name, is_active, 'CUSTOMER', false, created_at, updated_at
        FROM customers
        ON CONFLICT (email) DO NOTHING
    """)

    # Step 4: Create a temporary mapping table to track old customer_id to new user_id
    op.execute("""
        CREATE TEMP TABLE customer_user_mapping AS
        SELECT c.id as customer_id, u.id as user_id
        FROM customers c
        JOIN users u ON c.username = u.username AND c.email = u.email
    """)

    # Step 5: Add user_id columns to related tables (nullable first)
    op.add_column('addresses', sa.Column('user_id', sa.Integer(), nullable=True))
    op.add_column('customer_Sessions', sa.Column('user_id', sa.Integer(), nullable=True))
    op.add_column('orders', sa.Column('user_id', sa.Integer(), nullable=True))
    op.add_column('shopping_carts', sa.Column('user_id', sa.Integer(), nullable=True))

    # Step 6: Delete orphaned records (records with no matching customer)
    op.execute("""
        DELETE FROM addresses
        WHERE customer_id NOT IN (SELECT id FROM customers)
    """)

    op.execute("""
        DELETE FROM "customer_Sessions"
        WHERE customer_id NOT IN (SELECT id FROM customers)
    """)

    op.execute("""
        DELETE FROM orders
        WHERE customer_id NOT IN (SELECT id FROM customers)
    """)

    op.execute("""
        DELETE FROM shopping_carts
        WHERE customer_id NOT IN (SELECT id FROM customers)
    """)

    # Step 7: Migrate foreign key data using the mapping
    op.execute("""
        UPDATE addresses a
        SET user_id = m.user_id
        FROM customer_user_mapping m
        WHERE a.customer_id = m.customer_id
    """)

    op.execute("""
        UPDATE "customer_Sessions" cs
        SET user_id = m.user_id
        FROM customer_user_mapping m
        WHERE cs.customer_id = m.customer_id
    """)

    op.execute("""
        UPDATE orders o
        SET user_id = m.user_id
        FROM customer_user_mapping m
        WHERE o.customer_id = m.customer_id
    """)

    op.execute("""
        UPDATE shopping_carts sc
        SET user_id = m.user_id
        FROM customer_user_mapping m
        WHERE sc.customer_id = m.customer_id
    """)

    # Step 7b: Delete any remaining records with NULL user_id (shouldn't happen, but safety check)
    op.execute("DELETE FROM addresses WHERE user_id IS NULL")
    op.execute('DELETE FROM "customer_Sessions" WHERE user_id IS NULL')
    op.execute("DELETE FROM orders WHERE user_id IS NULL")
    op.execute("DELETE FROM shopping_carts WHERE user_id IS NULL")

    # Step 8: Make user_id columns NOT NULL now that data is migrated
    op.alter_column('addresses', 'user_id', nullable=False)
    op.alter_column('customer_Sessions', 'user_id', nullable=False)
    op.alter_column('orders', 'user_id', nullable=False)
    op.alter_column('shopping_carts', 'user_id', nullable=False)

    # Step 9: Drop old foreign key constraints
    op.drop_constraint('addresses_customer_id_fkey', 'addresses', type_='foreignkey')
    op.drop_constraint('customer_Sessions_customer_id_fkey', 'customer_Sessions', type_='foreignkey')
    op.drop_constraint('orders_customer_id_fkey', 'orders', type_='foreignkey')
    op.drop_constraint('shopping_carts_customer_id_fkey', 'shopping_carts', type_='foreignkey')

    # Step 10: Create new foreign key constraints
    op.create_foreign_key('addresses_user_id_fkey', 'addresses', 'users', ['user_id'], ['id'])
    op.create_foreign_key('customer_Sessions_user_id_fkey', 'customer_Sessions', 'users', ['user_id'], ['id'])
    op.create_foreign_key('orders_user_id_fkey', 'orders', 'users', ['user_id'], ['id'])
    op.create_foreign_key('shopping_carts_user_id_fkey', 'shopping_carts', 'users', ['user_id'], ['id'])

    # Step 11: Drop old customer_id columns
    op.drop_column('addresses', 'customer_id')
    op.drop_column('customer_Sessions', 'customer_id')
    op.drop_column('orders', 'customer_id')
    op.drop_column('shopping_carts', 'customer_id')

    # Step 12: Add is_visible column to reviews with default True
    op.add_column('reviews', sa.Column('is_visible', sa.Boolean(), server_default='true', nullable=False))

    # Step 12b: Drop the old reviews foreign key to customers and recreate to users
    op.drop_constraint('reviews_user_id_fkey', 'reviews', type_='foreignkey')
    op.create_foreign_key('reviews_user_id_fkey', 'reviews', 'users', ['user_id'], ['id'])

    # Step 13: Drop the customers table (data already migrated)
    op.drop_index('ix_customers_email', table_name='customers')
    op.drop_index('ix_customers_id', table_name='customers')
    op.drop_index('ix_customers_username', table_name='customers')
    op.drop_table('customers')

    # Step 14: Delete any users without username or password_hash (old users table records)
    op.execute("DELETE FROM users WHERE username IS NULL OR password_hash IS NULL")

    # Step 15: Make username and password_hash NOT NULL now that all data is migrated
    op.alter_column('users', 'username', nullable=False)
    op.alter_column('users', 'password_hash', nullable=False)

    # Step 16: Create unique index on username
    op.create_index('ix_users_username', 'users', ['username'], unique=True)


def downgrade() -> None:
    """Downgrade schema - WARNING: This will lose role and superadmin data!"""

    # Note: This downgrade is provided for completeness but may result in data loss
    # It's recommended to backup your database before running this downgrade

    # Recreate customers table
    op.create_table('customers',
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('username', sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column('password_hash', sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column('email', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column('full_name', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column('is_active', sa.BOOLEAN(), autoincrement=False, nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=True),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
        sa.PrimaryKeyConstraint('id', name='customers_pkey')
    )
    op.create_index('ix_customers_username', 'customers', ['username'], unique=True)
    op.create_index('ix_customers_id', 'customers', ['id'], unique=False)
    op.create_index('ix_customers_email', 'customers', ['email'], unique=True)

    # Migrate users with role='CUSTOMER' back to customers table
    op.execute("""
        INSERT INTO customers (id, username, password_hash, email, full_name, is_active, created_at, updated_at)
        SELECT id, username, password_hash, email, full_name, is_active, created_at, updated_at
        FROM users
        WHERE role = 'CUSTOMER'
    """)

    # Add customer_id columns back
    op.add_column('addresses', sa.Column('customer_id', sa.INTEGER(), nullable=True))
    op.add_column('customer_Sessions', sa.Column('customer_id', sa.INTEGER(), nullable=True))
    op.add_column('orders', sa.Column('customer_id', sa.INTEGER(), nullable=True))
    op.add_column('shopping_carts', sa.Column('customer_id', sa.INTEGER(), nullable=True))

    # Migrate foreign keys back
    op.execute("UPDATE addresses SET customer_id = user_id")
    op.execute('UPDATE "customer_Sessions" SET customer_id = user_id')
    op.execute("UPDATE orders SET customer_id = user_id")
    op.execute("UPDATE shopping_carts SET customer_id = user_id")

    # Make customer_id NOT NULL
    op.alter_column('addresses', 'customer_id', nullable=False)
    op.alter_column('customer_Sessions', 'customer_id', nullable=False)
    op.alter_column('orders', 'customer_id', nullable=False)
    op.alter_column('shopping_carts', 'customer_id', nullable=False)

    # Drop new foreign keys
    op.drop_constraint('addresses_user_id_fkey', 'addresses', type_='foreignkey')
    op.drop_constraint('customer_Sessions_user_id_fkey', 'customer_Sessions', type_='foreignkey')
    op.drop_constraint('orders_user_id_fkey', 'orders', type_='foreignkey')
    op.drop_constraint('shopping_carts_user_id_fkey', 'shopping_carts', type_='foreignkey')

    # Create old foreign keys
    op.create_foreign_key('addresses_customer_id_fkey', 'addresses', 'customers', ['customer_id'], ['id'])
    op.create_foreign_key('customer_Sessions_customer_id_fkey', 'customer_Sessions', 'customers', ['customer_id'], ['id'])
    op.create_foreign_key('orders_customer_id_fkey', 'orders', 'customers', ['customer_id'], ['id'])
    op.create_foreign_key('shopping_carts_customer_id_fkey', 'shopping_carts', 'customers', ['customer_id'], ['id'])

    # Drop user_id columns
    op.drop_column('addresses', 'user_id')
    op.drop_column('customer_Sessions', 'user_id')
    op.drop_column('orders', 'user_id')
    op.drop_column('shopping_carts', 'user_id')

    # Drop is_visible from reviews
    op.drop_column('reviews', 'is_visible')

    # Drop new columns from users
    op.drop_index('ix_users_username', table_name='users')
    op.drop_column('users', 'updated_at')
    op.drop_column('users', 'is_superadmin')
    op.drop_column('users', 'role')
    op.drop_column('users', 'is_active')
    op.drop_column('users', 'full_name')
    op.drop_column('users', 'password_hash')
    op.drop_column('users', 'username')

    # Make name NOT NULL again
    op.alter_column('users', 'name', existing_type=sa.VARCHAR(), nullable=False)

    # Drop the UserRole enum type
    user_role_enum = postgresql.ENUM('CUSTOMER', 'ADMIN', 'SUPERADMIN', name='userrole')
    user_role_enum.drop(op.get_bind(), checkfirst=True)
