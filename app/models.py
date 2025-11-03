from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from .database import Base


class UserRole(str, enum.Enum):
    """Enum for user roles."""

    CUSTOMER = "customer"
    ADMIN = "admin"
    SUPERADMIN = "superadmin"


class User(Base):
    """Represents a user in the database with authentication and role-based access."""

    __tablename__ = "users"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Required Fields - Authentication
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)

    # Required Fields - Profile
    email = Column(String, unique=True, index=True, nullable=False)

    # Optional Fields - Profile
    full_name = Column(String, nullable=True)
    name = Column(String, nullable=True)  # Legacy field from old users table
    phone_number = Column(String, nullable=True)
    address = Column(String, nullable=True)

    # Status and Role Fields
    is_active = Column(Boolean, default=True, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.CUSTOMER, nullable=False)
    is_superadmin = Column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    sessions = relationship(
        "CustomerSession", back_populates="user", cascade="all, delete-orphan"
    )
    shopping_carts = relationship(
        "ShoppingCart", back_populates="user", cascade="all, delete-orphan"
    )
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    addresses = relationship(
        "Address", back_populates="user", cascade="all, delete-orphan"
    )
    reviews = relationship(
        "Review", back_populates="user", cascade="all, delete-orphan"
    )


class CustomerSession(Base):
    """Represents a user login session."""

    __tablename__ = "customer_Sessions"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign Key
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Session Information
    session_id = Column(String, unique=True, index=True, nullable=False)
    ip_address = Column(String, nullable=True)

    # Timestamps
    login_time = Column(DateTime(timezone=True), server_default=func.now())
    logout_time = Column(DateTime(timezone=True), nullable=True)

    # Session Status
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationship
    user = relationship("User", back_populates="sessions")


class Product(Base):
    """Represents a product in the inventory."""

    __tablename__ = "products"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Product Information
    sku = Column(String, unique=True, index=True, nullable=False)  # Stock Keeping Unit
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)  # Decimal with 2 decimal places
    # NOTE: stock quantity is tracked in the Inventory table (one-to-one). The
    # `quantity` column was removed to make Inventory the single source of truth.

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    categories = relationship("ProductCategory", back_populates="product")
    cart_items = relationship("ShoppingCartItem", back_populates="product")
    reviews = relationship(
        "Review", back_populates="product", cascade="all, delete-orphan"
    )
    # inventory = relationship("Inventory", back_populates="product", uselist=False, cascade="all, delete-orphan")


class ProductCategory(Base):
    """Represents a product category."""

    __tablename__ = "product_categories"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign Key
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    # Category Information
    category_id = Column(Integer, nullable=False, index=True)
    category_name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship
    product = relationship("Product", back_populates="categories")


class ShoppingCart(Base):
    """Represents a shopping cart for a user."""

    __tablename__ = "shopping_carts"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign Key
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Cart Information
    last_modified = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="shopping_carts")
    items = relationship(
        "ShoppingCartItem", back_populates="cart", cascade="all, delete-orphan"
    )
    orders = relationship("Order", back_populates="cart")


class ShoppingCartItem(Base):
    """Represents an item in a shopping cart."""

    __tablename__ = "shopping_cart_items"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign Keys
    cart_id = Column(Integer, ForeignKey("shopping_carts.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    # Item Information
    quantity = Column(Integer, nullable=False, default=1)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    cart = relationship("ShoppingCart", back_populates="items")
    product = relationship("Product", back_populates="cart_items")


class Order(Base):
    """Represents a user order."""

    __tablename__ = "orders"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    cart_id = Column(Integer, ForeignKey("shopping_carts.id"), nullable=True)

    # Order Information
    address = Column(Text, nullable=False)
    order_status = Column(String, nullable=False, default="pending")
    total_amount = Column(Numeric(10, 2), nullable=True)

    # Timestamps
    order_date = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="orders")
    cart = relationship("ShoppingCart", back_populates="orders")
    payments = relationship(
        "Payment", back_populates="order", cascade="all, delete-orphan"
    )
    tracking_history = relationship(
        "OrderTracking", back_populates="order", cascade="all, delete-orphan"
    )


class Address(Base):
    """Represents a user address."""

    __tablename__ = "addresses"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign Key
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Address Information
    address = Column(Text, nullable=False)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    country = Column(String, nullable=False)
    postal_code = Column(String, nullable=True)
    is_default = Column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship
    user = relationship("User", back_populates="addresses")


class Review(Base):
    """Represents a product review by a user."""

    __tablename__ = "reviews"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    # Review Information
    rating = Column(Integer, nullable=False)  # 1-5 stars
    comment = Column(Text, nullable=True)
    is_visible = Column(Boolean, default=True, nullable=False)  # For review moderation

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="reviews")
    product = relationship("Product", back_populates="reviews")


class Inventory(Base):
    """Represents inventory tracking for products."""

    __tablename__ = "inventory"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign Key (One-to-One with Product)
    product_id = Column(Integer, ForeignKey("products.id"), unique=True, nullable=False)

    # Inventory Information
    quantity_in_stock = Column(Integer, nullable=False, default=0)
    reorder_level = Column(Integer, nullable=False, default=10)
    last_restocked_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship (One-to-One)
    # product = relationship("Product", back_populates="inventory", uselist=False)


class Payment(Base):
    """Represents a payment for an order."""

    __tablename__ = "payments"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign Key
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)

    # Payment Information
    transaction_id = Column(String, unique=True, nullable=False, index=True)
    payment_status = Column(String, nullable=False, default="pending")
    amount_paid = Column(Numeric(10, 2), nullable=False)
    payment_date = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    order = relationship("Order", back_populates="payments")


class OrderTracking(Base):
    """Represents tracking information for an order."""

    __tablename__ = "order_tracking"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign Key
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)

    # Tracking Information
    status = Column(String, nullable=False)
    location = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    order = relationship("Order", back_populates="tracking_history")
