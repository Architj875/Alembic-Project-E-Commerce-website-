from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from enum import Enum

from pydantic import BaseModel, EmailStr, Field, validator


# User Role Enum
class UserRoleEnum(str, Enum):
    """Enum for user roles."""
    CUSTOMER = "customer"
    ADMIN = "admin"
    SUPERADMIN = "superadmin"


# Unified User Schemas (merged from User and Customer)

class UserSignup(BaseModel):
    """Schema for user signup (request model)."""
    username: str
    password: str = Field(..., min_length=8, max_length=128)
    email: EmailStr
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None

    @validator('password')
    def validate_password_length(cls, v):
        """Validate password doesn't exceed bcrypt's 72-byte limit when encoded."""
        if isinstance(v, str):
            password_bytes = v.encode('utf-8')
            if len(password_bytes) > 72:
                raise ValueError(
                    'Password is too long when encoded as UTF-8. '
                    'Please use a shorter password (max 72 bytes).'
                )
        return v


class UserLogin(BaseModel):
    """Schema for user login (request model)."""
    username: str
    password: str


class UserUpdate(BaseModel):
    """Schema for updating a user (request model)."""
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    """Schema for user response (response model)."""
    id: int
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    is_active: bool
    role: UserRoleEnum
    is_superadmin: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        """Pydantic configuration."""
        orm_mode = True


class TokenResponse(BaseModel):
    """Schema for authentication token response."""
    access_token: str
    token_type: str
    user: UserResponse


class UserSessionResponse(BaseModel):
    """Schema for user session response."""
    id: int
    user_id: int
    session_id: str
    ip_address: Optional[str] = None
    login_time: datetime
    logout_time: Optional[datetime] = None
    is_active: bool

    class Config:
        """Pydantic configuration."""
        orm_mode = True


# Backward compatibility aliases
CustomerSignup = UserSignup
CustomerLogin = UserLogin
CustomerResponse = UserResponse
CustomerSessionResponse = UserSessionResponse


class LogoutResponse(BaseModel):
    """Schema for logout response."""
    message: str
    session_id: str
    logout_time: datetime


# Product Schemas

class ProductCreate(BaseModel):
    """Schema for creating a product (request model)."""
    sku: str = Field(..., description="Stock Keeping Unit - unique identifier")
    name: str = Field(..., description="Product name")
    description: Optional[str] = Field(None, description="Product description")
    price: Decimal = Field(..., gt=0, description="Product price (must be greater than 0)")
    # Inventory is managed separately via the Inventory endpoints.


class ProductUpdate(BaseModel):
    """Schema for updating a product (request model)."""
    name: Optional[str] = Field(None, description="Product name")
    description: Optional[str] = Field(None, description="Product description")
    price: Optional[Decimal] = Field(None, gt=0, description="Product price (must be greater than 0)")
    # quantity removed; inventory changes should be made through inventory endpoints.


class ProductResponse(BaseModel):
    """Schema for product response (response model)."""
    id: int
    sku: str
    name: str
    description: Optional[str] = None
    price: Decimal
    # quantity removed; use InventoryResponse for stock information
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        """Pydantic configuration."""
        orm_mode = True


# Product Category Schemas

class ProductCategoryCreate(BaseModel):
    """Schema for creating a product category (request model)."""
    product_id: int = Field(..., description="Product ID")
    category_id: int = Field(..., description="Category ID")
    category_name: str = Field(..., description="Category name")
    description: Optional[str] = Field(None, description="Category description")
    is_active: bool = Field(True, description="Category active status")


class ProductCategoryUpdate(BaseModel):
    """Schema for updating a product category (request model)."""
    category_name: Optional[str] = Field(None, description="Category name")
    description: Optional[str] = Field(None, description="Category description")
    is_active: Optional[bool] = Field(None, description="Category active status")


class ProductCategoryResponse(BaseModel):
    """Schema for product category response (response model)."""
    id: int
    product_id: int
    category_id: int
    category_name: str
    description: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        """Pydantic configuration."""
        orm_mode = True


# Shopping Cart Schemas

class ShoppingCartItemCreate(BaseModel):
    """Schema for adding an item to cart (request model)."""
    product_id: int = Field(..., description="Product ID")
    quantity: int = Field(1, ge=1, description="Quantity (must be >= 1)")


class ShoppingCartItemUpdate(BaseModel):
    """Schema for updating a cart item (request model)."""
    quantity: int = Field(..., ge=1, description="Quantity (must be >= 1)")


class ShoppingCartItemResponse(BaseModel):
    """Schema for cart item response (response model)."""
    id: int
    cart_id: int
    product_id: int
    quantity: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        """Pydantic configuration."""
        orm_mode = True


class ShoppingCartResponse(BaseModel):
    """Schema for shopping cart response (response model)."""
    id: int
    last_modified: datetime
    created_at: datetime
    items: List[ShoppingCartItemResponse] = []

    class Config:
        """Pydantic configuration."""
        orm_mode = True


# Order Schemas

class OrderCreate(BaseModel):
    """Schema for creating an order (request model)."""
    cart_id: int = Field(..., description="Shopping cart ID")
    address: str = Field(..., description="Delivery address")


class OrderUpdate(BaseModel):
    """Schema for updating an order (request model)."""
    address: Optional[str] = Field(None, description="Delivery address")
    order_status: Optional[str] = Field(
        None,
        description="Order status (pending, confirmed, shipped, delivered, cancelled)"
    )


class OrderResponse(BaseModel):
    """Schema for order response (response model)."""
    id: int
    #customer_id: int
    cart_id: Optional[int] = None
    address: str
    order_status: str
    total_amount: Optional[Decimal] = None
    order_date: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        """Pydantic configuration."""
        orm_mode = True


# Address Schemas

class AddressCreate(BaseModel):
    """Schema for creating an address (request model)."""
    address: str = Field(..., description="Street address")
    city: str = Field(..., description="City name")
    state: str = Field(..., description="State/Province")
    country: str = Field(..., description="Country name")
    postal_code: Optional[str] = Field(None, description="Postal/ZIP code")
    is_default: bool = Field(False, description="Set as default address")


class AddressUpdate(BaseModel):
    """Schema for updating an address (request model)."""
    address: Optional[str] = Field(None, description="Street address")
    city: Optional[str] = Field(None, description="City name")
    state: Optional[str] = Field(None, description="State/Province")
    country: Optional[str] = Field(None, description="Country name")
    postal_code: Optional[str] = Field(None, description="Postal/ZIP code")
    is_default: Optional[bool] = Field(None, description="Set as default address")


class AddressResponse(BaseModel):
    """Schema for address response (response model)."""
    id: int
    user_id: int
    address: str
    city: str
    state: str
    country: str
    postal_code: Optional[str] = None
    is_default: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        """Pydantic configuration."""
        orm_mode = True


# Review Schemas

class ReviewCreate(BaseModel):
    """Schema for creating a review (request model)."""
    product_id: int = Field(..., description="Product ID")
    rating: int = Field(..., ge=1, le=5, description="Rating (1-5 stars)")
    comment: Optional[str] = Field(None, description="Review comment")


class ReviewUpdate(BaseModel):
    """Schema for updating a review (request model)."""
    rating: Optional[int] = Field(None, ge=1, le=5, description="Rating (1-5 stars)")
    comment: Optional[str] = Field(None, description="Review comment")


class ReviewResponse(BaseModel):
    """Schema for review response (response model)."""
    id: int
    user_id: int
    product_id: int
    rating: int
    comment: Optional[str] = None
    is_visible: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        """Pydantic configuration."""
        orm_mode = True


# Inventory Schemas

class InventoryCreate(BaseModel):
    """Schema for creating inventory (request model)."""
    product_id: int = Field(..., description="Product ID")
    quantity_in_stock: int = Field(0, ge=0, description="Quantity in stock")
    reorder_level: int = Field(10, ge=0, description="Reorder level threshold")


class InventoryUpdate(BaseModel):
    """Schema for updating inventory (request model)."""
    quantity_in_stock: Optional[int] = Field(None, ge=0, description="Quantity in stock")
    reorder_level: Optional[int] = Field(None, ge=0, description="Reorder level threshold")


class InventoryRestock(BaseModel):
    """Schema for restocking inventory (request model)."""
    quantity_to_add: int = Field(..., gt=0, description="Quantity to add to stock")


class InventoryResponse(BaseModel):
    """Schema for inventory response (response model)."""
    id: int
    product_id: int
    quantity_in_stock: int
    reorder_level: int
    last_restocked_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        """Pydantic configuration."""
        orm_mode = True


# Payment Schemas

class PaymentCreate(BaseModel):
    """Schema for creating a payment (request model)."""
    order_id: int = Field(..., description="Order ID")
    transaction_id: str = Field(..., description="Unique transaction ID")
    amount_paid: Decimal = Field(..., gt=0, description="Amount paid")
    payment_status: str = Field("pending", description="Payment status")


class PaymentUpdate(BaseModel):
    """Schema for updating a payment (request model)."""
    payment_status: Optional[str] = Field(None, description="Payment status")
    payment_date: Optional[datetime] = Field(None, description="Payment date")


class PaymentResponse(BaseModel):
    """Schema for payment response (response model)."""
    id: int
    order_id: int
    transaction_id: str
    payment_status: str
    amount_paid: Decimal
    payment_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        """Pydantic configuration."""
        orm_mode = True


# Order Tracking Schemas

class OrderTrackingCreate(BaseModel):
    """Schema for creating order tracking entry (request model)."""
    order_id: int = Field(..., description="Order ID")
    status: str = Field(..., description="Order status")
    location: Optional[str] = Field(None, description="Current location")
    notes: Optional[str] = Field(None, description="Additional notes")


class OrderTrackingUpdate(BaseModel):
    """Schema for updating order tracking entry (request model)."""
    status: Optional[str] = Field(None, description="Order status")
    location: Optional[str] = Field(None, description="Current location")
    notes: Optional[str] = Field(None, description="Additional notes")


class OrderTrackingResponse(BaseModel):
    """Schema for order tracking response (response model)."""
    id: int
    order_id: int
    status: str
    location: Optional[str] = None
    notes: Optional[str] = None
    timestamp: datetime
    created_at: datetime

    class Config:
        """Pydantic configuration."""
        orm_mode = True


# Superadmin Schemas

class UserRoleUpdate(BaseModel):
    """Schema for updating user role (superadmin only)."""
    role: UserRoleEnum
    is_superadmin: Optional[bool] = False


class ReviewModerationUpdate(BaseModel):
    """Schema for moderating reviews (superadmin only)."""
    is_visible: bool


class SuperadminProductCreate(BaseModel):
    """Schema for creating a product (superadmin only)."""
    name: str
    description: Optional[str] = None
    price: Decimal = Field(..., gt=0, description="Product price must be greater than 0")
    sku: str
    # quantity removed; inventory should be created/updated via Inventory APIs


class SuperadminProductUpdate(BaseModel):
    """Schema for updating a product (superadmin only)."""
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, gt=0, description="Product price must be greater than 0")
    sku: Optional[str] = None
    # quantity removed; inventory should be created/updated via Inventory APIs
