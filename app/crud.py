from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy.orm import Session

from . import models, schemas
from .auth import get_password_hash, generate_session_id


# User CRUD Operations (merged from User and Customer)

def get_user(db: Session, user_id: int) -> Optional[models.User]:
    """
    Fetches a single user by their unique ID.

    Args:
        db: The database session.
        user_id: The ID of the user to fetch.

    Returns:
        The User model instance if found, otherwise None.
    """
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    """
    Fetches a user by their username.

    Args:
        db: The database session.
        username: The username of the user to fetch.

    Returns:
        The User model instance if found, otherwise None.
    """
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """
    Fetches a single user by their email address.

    Args:
        db: The database session.
        email: The email of the user to fetch.

    Returns:
        The User model instance if found, otherwise None.
    """
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(
    db: Session, skip: int = 0, limit: int = 100, username: Optional[str] = None,
    role: Optional[models.UserRole] = None
) -> List[models.User]:
    """
    Fetches a list of users with optional filtering and pagination.

    Args:
        db: The database session.
        skip: The number of records to skip for pagination.
        limit: The maximum number of records to return.
        username: An optional username to filter users by (case-insensitive).
        role: An optional role to filter users by.

    Returns:
        A list of User model instances.
    """
    query = db.query(models.User)
    if username:
        query = query.filter(models.User.username.ilike(f"%{username}%"))
    if role:
        query = query.filter(models.User.role == role)
    return query.offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserSignup, role: models.UserRole = models.UserRole.CUSTOMER) -> models.User:
    """
    Creates a new user with hashed password.

    Args:
        db: The database session.
        user: The Pydantic schema containing the user's signup data.
        role: The role to assign to the user (default: CUSTOMER).

    Returns:
        The newly created User model instance.
    """
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        password_hash=hashed_password,
        email=user.email,
        full_name=user.full_name,
        phone_number=user.phone_number,
        address=user.address,
        role=role,
        is_superadmin=(role == models.UserRole.SUPERADMIN)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(
    db: Session, user_id: int, user_update: schemas.UserUpdate
) -> Optional[models.User]:
    """
    Updates an existing user's information.

    Args:
        db: The database session.
        user_id: The ID of the user to update.
        user_update: A Pydantic schema with the fields to update.

    Returns:
        The updated User model instance, or None if the user was not found.
    """
    db_user = get_user(db, user_id)
    if not db_user:
        return None

    update_data = user_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)
    return db_user


def update_user_role(
    db: Session, user_id: int, role: models.UserRole, is_superadmin: bool = False
) -> Optional[models.User]:
    """
    Updates a user's role and superadmin status (superadmin only).

    Args:
        db: The database session.
        user_id: The ID of the user to update.
        role: The new role to assign.
        is_superadmin: Whether the user should be a superadmin.

    Returns:
        The updated User model instance, or None if the user was not found.
    """
    db_user = get_user(db, user_id)
    if not db_user:
        return None

    db_user.role = role
    db_user.is_superadmin = is_superadmin

    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> Optional[models.User]:
    """
    Deletes a user from the database (superadmin only).

    Args:
        db: The database session.
        user_id: The ID of the user to delete.

    Returns:
        The deleted User model instance, or None if not found.
    """
    db_user = get_user(db, user_id)
    if not db_user:
        return None

    db.delete(db_user)
    db.commit()
    return db_user


def delete_user(db: Session, user_id: int) -> Optional[models.User]:
    """
    Deletes a user from the database.

    Args:
        db: The database session.
        user_id: The ID of the user to delete.

    Returns:
        The deleted User model instance, or None if the user was not found.
    """
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    db.delete(db_user)
    db.commit()
    return db_user


# Backward compatibility aliases
get_customer_by_id = get_user
get_customer_by_username = get_user_by_username
create_customer = create_user


# User Session CRUD Operations

def create_user_session(
    db: Session,
    user_id: int,
    session_id: str,
    ip_address: Optional[str] = None
) -> models.CustomerSession:
    """
    Creates a new user session.

    Args:
        db: The database session.
        user_id: The ID of the user.
        session_id: The unique session ID.
        ip_address: The IP address of the user.

    Returns:
        The newly created CustomerSession model instance.
    """
    db_session = models.CustomerSession(
        user_id=user_id,
        session_id=session_id,
        ip_address=ip_address,
        is_active=True
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


def get_active_session(db: Session, session_id: str) -> Optional[models.CustomerSession]:
    """
    Fetches an active session by session ID.

    Args:
        db: The database session.
        session_id: The session ID to fetch.

    Returns:
        The CustomerSession model instance if found and active, otherwise None.
    """
    return db.query(models.CustomerSession).filter(
        models.CustomerSession.session_id == session_id,
        models.CustomerSession.is_active == True
    ).first()


def end_user_session(db: Session, session_id: str) -> Optional[models.CustomerSession]:
    """
    Ends a user session by setting logout time and marking as inactive.

    Args:
        db: The database session.
        session_id: The session ID to end.

    Returns:
        The updated CustomerSession model instance, or None if not found.
    """
    db_session = get_active_session(db, session_id)
    if not db_session:
        return None

    from datetime import timezone
    db_session.logout_time = datetime.now(timezone.utc)
    db_session.is_active = False
    db.commit()
    db.refresh(db_session)
    return db_session


def get_user_sessions(
    db: Session,
    user_id: int,
    active_only: bool = False
) -> List[models.CustomerSession]:
    """
    Fetches all sessions for a user.

    Args:
        db: The database session.
        user_id: The ID of the user.
        active_only: If True, only return active sessions.

    Returns:
        A list of CustomerSession model instances.
    """
    query = db.query(models.CustomerSession).filter(
        models.CustomerSession.user_id == user_id
    )
    if active_only:
        query = query.filter(models.CustomerSession.is_active == True)
    return query.order_by(models.CustomerSession.login_time.desc()).all()


# Backward compatibility aliases for session functions
create_customer_session = create_user_session
end_customer_session = end_user_session
get_customer_sessions = get_user_sessions


# Product CRUD Operations

def get_product(db: Session, product_id: int) -> Optional[models.Product]:
    """
    Fetches a single product by its ID.

    Args:
        db: The database session.
        product_id: The ID of the product to fetch.

    Returns:
        The Product model instance if found, otherwise None.
    """
    return db.query(models.Product).filter(models.Product.id == product_id).first()


def get_product_by_sku(db: Session, sku: str) -> Optional[models.Product]:
    """
    Fetches a single product by its SKU.

    Args:
        db: The database session.
        sku: The SKU of the product to fetch.

    Returns:
        The Product model instance if found, otherwise None.
    """
    return db.query(models.Product).filter(models.Product.sku == sku).first()


def get_products(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    name: Optional[str] = None
) -> List[models.Product]:
    """
    Fetches a list of products with optional filtering and pagination.

    Args:
        db: The database session.
        skip: The number of records to skip for pagination.
        limit: The maximum number of records to return.
        name: An optional name to filter products by (case-insensitive).

    Returns:
        A list of Product model instances.
    """
    query = db.query(models.Product)
    if name:
        query = query.filter(models.Product.name.ilike(f"%{name}%"))
    return query.offset(skip).limit(limit).all()


def create_product(db: Session, product: schemas.ProductCreate) -> models.Product:
    """
    Creates a new product in the database.

    Args:
        db: The database session.
        product: The Pydantic schema containing the product's creation data.

    Returns:
        The newly created Product model instance.
    """
    db_product = models.Product(
        sku=product.sku,
        name=product.name,
        description=product.description,
        price=product.price,
        quantity=product.quantity
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def update_product(
    db: Session,
    product_id: int,
    product_update: schemas.ProductUpdate
) -> Optional[models.Product]:
    """
    Updates an existing product's information.

    Args:
        db: The database session.
        product_id: The ID of the product to update.
        product_update: A Pydantic schema with the fields to update.

    Returns:
        The updated Product model instance, or None if the product was not found.
    """
    db_product = get_product(db, product_id)
    if not db_product:
        return None

    update_data = product_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_product, key, value)

    db.commit()
    db.refresh(db_product)
    return db_product


def delete_product(db: Session, product_id: int) -> Optional[models.Product]:
    """
    Deletes a product from the database.

    Args:
        db: The database session.
        product_id: The ID of the product to delete.

    Returns:
        The deleted Product model instance, or None if the product was not found.
    """
    db_product = get_product(db, product_id)
    if not db_product:
        return None
    db.delete(db_product)
    db.commit()
    return db_product


# ============================================================================
# Product Category CRUD Operations
# ============================================================================

def get_product_category(db: Session, category_id: int) -> Optional[models.ProductCategory]:
    """
    Retrieves a product category by its ID.

    Args:
        db: The database session.
        category_id: The ID of the product category to fetch.

    Returns:
        The ProductCategory model instance, or None if not found.
    """
    return db.query(models.ProductCategory).filter(
        models.ProductCategory.id == category_id
    ).first()


def get_product_categories(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    product_id: Optional[int] = None,
    is_active: Optional[bool] = None
) -> List[models.ProductCategory]:
    """
    Retrieves a list of product categories with optional filtering.

    Args:
        db: The database session.
        skip: Number of records to skip (for pagination).
        limit: Maximum number of records to return.
        product_id: Optional product ID to filter by.
        is_active: Optional active status to filter by.

    Returns:
        A list of ProductCategory model instances.
    """
    query = db.query(models.ProductCategory)

    if product_id is not None:
        query = query.filter(models.ProductCategory.product_id == product_id)

    if is_active is not None:
        query = query.filter(models.ProductCategory.is_active == is_active)

    return query.offset(skip).limit(limit).all()


def create_product_category(
    db: Session,
    category: schemas.ProductCategoryCreate
) -> models.ProductCategory:
    """
    Creates a new product category in the database.

    Args:
        db: The database session.
        category: The Pydantic schema containing the category's creation data.

    Returns:
        The newly created ProductCategory model instance.
    """
    db_category = models.ProductCategory(
        product_id=category.product_id,
        category_id=category.category_id,
        category_name=category.category_name,
        description=category.description,
        is_active=category.is_active
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def update_product_category(
    db: Session,
    category_id: int,
    category_update: schemas.ProductCategoryUpdate
) -> Optional[models.ProductCategory]:
    """
    Updates an existing product category's information.

    Args:
        db: The database session.
        category_id: The ID of the category to update.
        category_update: A Pydantic schema with the fields to update.

    Returns:
        The updated ProductCategory model instance, or None if not found.
    """
    db_category = get_product_category(db, category_id)
    if not db_category:
        return None

    update_data = category_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_category, key, value)

    db.commit()
    db.refresh(db_category)
    return db_category


def delete_product_category(
    db: Session,
    category_id: int
) -> Optional[models.ProductCategory]:
    """
    Deletes a product category from the database.

    Args:
        db: The database session.
        category_id: The ID of the category to delete.

    Returns:
        The deleted ProductCategory model instance, or None if not found.
    """
    db_category = get_product_category(db, category_id)
    if not db_category:
        return None
    db.delete(db_category)
    db.commit()
    return db_category


# ============================================================================
# Shopping Cart CRUD Operations
# ============================================================================

def get_shopping_cart(db: Session, cart_id: int) -> Optional[models.ShoppingCart]:
    """
    Retrieves a shopping cart by its ID.

    Args:
        db: The database session.
        cart_id: The ID of the shopping cart to fetch.

    Returns:
        The ShoppingCart model instance, or None if not found.
    """
    return db.query(models.ShoppingCart).filter(
        models.ShoppingCart.id == cart_id
    ).first()


def get_user_cart(
    db: Session,
    user_id: int
) -> Optional[models.ShoppingCart]:
    """
    Retrieves the active shopping cart for a user.

    Args:
        db: The database session.
        user_id: The ID of the user.

    Returns:
        The ShoppingCart model instance, or None if not found.
    """
    return db.query(models.ShoppingCart).filter(
        models.ShoppingCart.user_id == user_id
    ).first()


def create_shopping_cart(
    db: Session,
    user_id: int
) -> models.ShoppingCart:
    """
    Creates a new shopping cart for a user.

    Args:
        db: The database session.
        user_id: The ID of the user.

    Returns:
        The newly created ShoppingCart model instance.
    """
    db_cart = models.ShoppingCart(user_id=user_id)
    db.add(db_cart)
    db.commit()
    db.refresh(db_cart)
    return db_cart


# Backward compatibility alias
get_customer_cart = get_user_cart


def add_item_to_cart(
    db: Session,
    cart_id: int,
    item: schemas.ShoppingCartItemCreate
) -> models.ShoppingCartItem:
    """
    Adds an item to a shopping cart or updates quantity if it exists.

    Args:
        db: The database session.
        cart_id: The ID of the shopping cart.
        item: The Pydantic schema containing the item data.

    Returns:
        The ShoppingCartItem model instance.
    """
    # Check if item already exists in cart
    existing_item = db.query(models.ShoppingCartItem).filter(
        models.ShoppingCartItem.cart_id == cart_id,
        models.ShoppingCartItem.product_id == item.product_id
    ).first()

    if existing_item:
        # Update quantity
        existing_item.quantity += item.quantity
        db.commit()
        db.refresh(existing_item)
        return existing_item
    else:
        # Create new item
        db_item = models.ShoppingCartItem(
            cart_id=cart_id,
            product_id=item.product_id,
            quantity=item.quantity
        )
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item


def update_cart_item(
    db: Session,
    item_id: int,
    item_update: schemas.ShoppingCartItemUpdate
) -> Optional[models.ShoppingCartItem]:
    """
    Updates a cart item's quantity.

    Args:
        db: The database session.
        item_id: The ID of the cart item to update.
        item_update: A Pydantic schema with the fields to update.

    Returns:
        The updated ShoppingCartItem model instance, or None if not found.
    """
    db_item = db.query(models.ShoppingCartItem).filter(
        models.ShoppingCartItem.id == item_id
    ).first()

    if not db_item:
        return None

    db_item.quantity = item_update.quantity
    db.commit()
    db.refresh(db_item)
    return db_item


def remove_item_from_cart(
    db: Session,
    item_id: int
) -> Optional[models.ShoppingCartItem]:
    """
    Removes an item from a shopping cart.

    Args:
        db: The database session.
        item_id: The ID of the cart item to remove.

    Returns:
        The deleted ShoppingCartItem model instance, or None if not found.
    """
    db_item = db.query(models.ShoppingCartItem).filter(
        models.ShoppingCartItem.id == item_id
    ).first()

    if not db_item:
        return None

    db.delete(db_item)
    db.commit()
    return db_item


def clear_cart(db: Session, cart_id: int) -> bool:
    """
    Removes all items from a shopping cart.

    Args:
        db: The database session.
        cart_id: The ID of the shopping cart.

    Returns:
        True if items were deleted, False otherwise.
    """
    db.query(models.ShoppingCartItem).filter(
        models.ShoppingCartItem.cart_id == cart_id
    ).delete()
    db.commit()
    return True


# ============================================================================
# Order CRUD Operations
# ============================================================================

def get_order(db: Session, order_id: int) -> Optional[models.Order]:
    """
    Retrieves an order by its ID.

    Args:
        db: The database session.
        order_id: The ID of the order to fetch.

    Returns:
        The Order model instance, or None if not found.
    """
    return db.query(models.Order).filter(models.Order.id == order_id).first()


def get_orders(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    order_status: Optional[str] = None
) -> List[models.Order]:
    """
    Retrieves a list of orders with optional filtering.

    Args:
        db: The database session.
        skip: Number of records to skip (for pagination).
        limit: Maximum number of records to return.
        user_id: Optional user ID to filter by.
        order_status: Optional order status to filter by.

    Returns:
        A list of Order model instances.
    """
    query = db.query(models.Order)

    if user_id is not None:
        query = query.filter(models.Order.user_id == user_id)

    if order_status is not None:
        query = query.filter(models.Order.order_status == order_status)

    return query.order_by(models.Order.order_date.desc()).offset(skip).limit(limit).all()


def create_order(
    db: Session,
    user_id: int,
    order: schemas.OrderCreate
) -> models.Order:
    """
    Creates a new order from a shopping cart.

    Args:
        db: The database session.
        user_id: The ID of the user.
        order: The Pydantic schema containing the order data.

    Returns:
        The newly created Order model instance.
    """
    # Get cart to calculate total
    cart = get_shopping_cart(db, order.cart_id)
    total_amount = Decimal("0.00")

    if cart and cart.items:
        for item in cart.items:
            product = get_product(db, item.product_id)
            if product:
                total_amount += product.price * item.quantity

    db_order = models.Order(
        user_id=user_id,
        cart_id=order.cart_id,
        address=order.address,
        order_status="pending",
        total_amount=total_amount
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


def update_order(
    db: Session,
    order_id: int,
    order_update: schemas.OrderUpdate
) -> Optional[models.Order]:
    """
    Updates an existing order's information.

    Args:
        db: The database session.
        order_id: The ID of the order to update.
        order_update: A Pydantic schema with the fields to update.

    Returns:
        The updated Order model instance, or None if not found.
    """
    db_order = get_order(db, order_id)
    if not db_order:
        return None

    update_data = order_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_order, key, value)

    db.commit()
    db.refresh(db_order)
    return db_order


def delete_order(db: Session, order_id: int) -> Optional[models.Order]:
    """
    Deletes an order from the database.

    Args:
        db: The database session.
        order_id: The ID of the order to delete.

    Returns:
        The deleted Order model instance, or None if not found.
    """
    db_order = get_order(db, order_id)
    if not db_order:
        return None
    db.delete(db_order)
    db.commit()
    return db_order


# ============================================================================
# Address CRUD Operations
# ============================================================================

def get_address(db: Session, address_id: int) -> Optional[models.Address]:
    """
    Retrieves an address by its ID.

    Args:
        db: The database session.
        address_id: The ID of the address to fetch.

    Returns:
        The Address model instance, or None if not found.
    """
    return db.query(models.Address).filter(models.Address.id == address_id).first()


def get_addresses(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None
) -> List[models.Address]:
    """
    Retrieves a list of addresses with optional filtering.

    Args:
        db: The database session.
        skip: Number of records to skip (for pagination).
        limit: Maximum number of records to return.
        user_id: Optional user ID to filter by.

    Returns:
        A list of Address model instances.
    """
    query = db.query(models.Address)

    if user_id is not None:
        query = query.filter(models.Address.user_id == user_id)

    return query.offset(skip).limit(limit).all()


def create_address(
    db: Session,
    user_id: int,
    address: schemas.AddressCreate
) -> models.Address:
    """
    Creates a new address for a user.

    Args:
        db: The database session.
        user_id: The ID of the user.
        address: The Pydantic schema containing the address data.

    Returns:
        The newly created Address model instance.
    """
    # If this is set as default, unset other default addresses
    if address.is_default:
        db.query(models.Address).filter(
            models.Address.user_id == user_id,
            models.Address.is_default == True
        ).update({"is_default": False})

    db_address = models.Address(
        user_id=user_id,
        address=address.address,
        city=address.city,
        state=address.state,
        country=address.country,
        postal_code=address.postal_code,
        is_default=address.is_default
    )
    db.add(db_address)
    db.commit()
    db.refresh(db_address)
    return db_address


def update_address(
    db: Session,
    address_id: int,
    address_update: schemas.AddressUpdate
) -> Optional[models.Address]:
    """
    Updates an existing address.

    Args:
        db: The database session.
        address_id: The ID of the address to update.
        address_update: A Pydantic schema with the fields to update.

    Returns:
        The updated Address model instance, or None if not found.
    """
    db_address = get_address(db, address_id)
    if not db_address:
        return None

    # If setting as default, unset other default addresses
    if address_update.is_default:
        db.query(models.Address).filter(
            models.Address.user_id == db_address.user_id,
            models.Address.is_default == True,
            models.Address.id != address_id
        ).update({"is_default": False})

    update_data = address_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_address, key, value)

    db.commit()
    db.refresh(db_address)
    return db_address


def delete_address(db: Session, address_id: int) -> Optional[models.Address]:
    """
    Deletes an address from the database.

    Args:
        db: The database session.
        address_id: The ID of the address to delete.

    Returns:
        The deleted Address model instance, or None if not found.
    """
    db_address = get_address(db, address_id)
    if not db_address:
        return None
    db.delete(db_address)
    db.commit()
    return db_address


# ============================================================================
# Review CRUD Operations
# ============================================================================

def get_review(db: Session, review_id: int) -> Optional[models.Review]:
    """
    Retrieves a review by its ID.

    Args:
        db: The database session.
        review_id: The ID of the review to fetch.

    Returns:
        The Review model instance, or None if not found.
    """
    return db.query(models.Review).filter(models.Review.id == review_id).first()


def get_reviews(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    product_id: Optional[int] = None,
    user_id: Optional[int] = None,
    min_rating: Optional[int] = None
) -> List[models.Review]:
    """
    Retrieves a list of reviews with optional filtering.

    Args:
        db: The database session.
        skip: Number of records to skip (for pagination).
        limit: Maximum number of records to return.
        product_id: Optional product ID to filter by.
        user_id: Optional user ID to filter by.
        min_rating: Optional minimum rating to filter by.

    Returns:
        A list of Review model instances.
    """
    query = db.query(models.Review)

    if product_id is not None:
        query = query.filter(models.Review.product_id == product_id)

    if user_id is not None:
        query = query.filter(models.Review.user_id == user_id)

    if min_rating is not None:
        query = query.filter(models.Review.rating >= min_rating)

    return query.order_by(models.Review.created_at.desc()).offset(skip).limit(limit).all()


def create_review(
    db: Session,
    user_id: int,
    review: schemas.ReviewCreate
) -> models.Review:
    """
    Creates a new review for a product.

    Args:
        db: The database session.
        user_id: The ID of the user creating the review.
        review: The Pydantic schema containing the review data.

    Returns:
        The newly created Review model instance.
    """
    db_review = models.Review(
        user_id=user_id,
        product_id=review.product_id,
        rating=review.rating,
        comment=review.comment
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review


def update_review(
    db: Session,
    review_id: int,
    review_update: schemas.ReviewUpdate
) -> Optional[models.Review]:
    """
    Updates an existing review.

    Args:
        db: The database session.
        review_id: The ID of the review to update.
        review_update: A Pydantic schema with the fields to update.

    Returns:
        The updated Review model instance, or None if not found.
    """
    db_review = get_review(db, review_id)
    if not db_review:
        return None

    update_data = review_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_review, key, value)

    db.commit()
    db.refresh(db_review)
    return db_review


def delete_review(db: Session, review_id: int) -> Optional[models.Review]:
    """
    Deletes a review from the database.

    Args:
        db: The database session.
        review_id: The ID of the review to delete.

    Returns:
        The deleted Review model instance, or None if not found.
    """
    db_review = get_review(db, review_id)
    if not db_review:
        return None
    db.delete(db_review)
    db.commit()
    return db_review


def moderate_review(db: Session, review_id: int, is_visible: bool) -> Optional[models.Review]:
    """
    Moderates a review by setting its visibility (superadmin only).

    Args:
        db: The database session.
        review_id: The ID of the review to moderate.
        is_visible: Whether the review should be visible.

    Returns:
        The updated Review model instance, or None if not found.
    """
    db_review = get_review(db, review_id)
    if not db_review:
        return None

    db_review.is_visible = is_visible
    db.commit()
    db.refresh(db_review)
    return db_review


def get_product_average_rating(db: Session, product_id: int) -> Optional[float]:
    """
    Calculates the average rating for a product.

    Args:
        db: The database session.
        product_id: The ID of the product.

    Returns:
        The average rating, or None if no reviews exist.
    """
    from sqlalchemy import func as sql_func

    result = db.query(sql_func.avg(models.Review.rating)).filter(
        models.Review.product_id == product_id
    ).scalar()

    return float(result) if result else None


# ============================================================================
# Inventory CRUD Operations
# ============================================================================

def get_inventory(db: Session, inventory_id: int) -> Optional[models.Inventory]:
    """
    Retrieves inventory by its ID.

    Args:
        db: The database session.
        inventory_id: The ID of the inventory to fetch.

    Returns:
        The Inventory model instance, or None if not found.
    """
    return db.query(models.Inventory).filter(
        models.Inventory.id == inventory_id
    ).first()


def get_inventory_by_product(
    db: Session,
    product_id: int
) -> Optional[models.Inventory]:
    """
    Retrieves inventory by product ID.

    Args:
        db: The database session.
        product_id: The ID of the product.

    Returns:
        The Inventory model instance, or None if not found.
    """
    return db.query(models.Inventory).filter(
        models.Inventory.product_id == product_id
    ).first()


def get_inventories(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    low_stock_only: bool = False
) -> List[models.Inventory]:
    """
    Retrieves a list of inventory records with optional filtering.

    Args:
        db: The database session.
        skip: Number of records to skip (for pagination).
        limit: Maximum number of records to return.
        low_stock_only: If True, only return items below reorder level.

    Returns:
        A list of Inventory model instances.
    """
    query = db.query(models.Inventory)

    if low_stock_only:
        # Filter for items where quantity is at or below reorder level
        from sqlalchemy import and_
        query = query.filter(
            models.Inventory.quantity_in_stock <= models.Inventory.reorder_level
        )

    return query.offset(skip).limit(limit).all()


def create_inventory(
    db: Session,
    inventory: schemas.InventoryCreate
) -> models.Inventory:
    """
    Creates a new inventory record for a product.

    Args:
        db: The database session.
        inventory: The Pydantic schema containing the inventory data.

    Returns:
        The newly created Inventory model instance.
    """
    db_inventory = models.Inventory(
        product_id=inventory.product_id,
        quantity_in_stock=inventory.quantity_in_stock,
        reorder_level=inventory.reorder_level,
        last_restocked_at=datetime.now() if inventory.quantity_in_stock > 0 else None
    )
    db.add(db_inventory)
    db.commit()
    db.refresh(db_inventory)
    return db_inventory


def update_inventory(
    db: Session,
    inventory_id: int,
    inventory_update: schemas.InventoryUpdate
) -> Optional[models.Inventory]:
    """
    Updates an existing inventory record.

    Args:
        db: The database session.
        inventory_id: The ID of the inventory to update.
        inventory_update: A Pydantic schema with the fields to update.

    Returns:
        The updated Inventory model instance, or None if not found.
    """
    db_inventory = get_inventory(db, inventory_id)
    if not db_inventory:
        return None

    update_data = inventory_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_inventory, key, value)

    db.commit()
    db.refresh(db_inventory)
    return db_inventory


def restock_inventory(
    db: Session,
    inventory_id: int,
    quantity_to_add: int
) -> Optional[models.Inventory]:
    """
    Restocks inventory by adding quantity.

    Args:
        db: The database session.
        inventory_id: The ID of the inventory to restock.
        quantity_to_add: The quantity to add to stock.

    Returns:
        The updated Inventory model instance, or None if not found.
    """
    db_inventory = get_inventory(db, inventory_id)
    if not db_inventory:
        return None

    db_inventory.quantity_in_stock += quantity_to_add
    db_inventory.last_restocked_at = datetime.now()

    db.commit()
    db.refresh(db_inventory)
    return db_inventory


def delete_inventory(db: Session, inventory_id: int) -> Optional[models.Inventory]:
    """
    Deletes an inventory record from the database.

    Args:
        db: The database session.
        inventory_id: The ID of the inventory to delete.

    Returns:
        The deleted Inventory model instance, or None if not found.
    """
    db_inventory = get_inventory(db, inventory_id)
    if not db_inventory:
        return None
    db.delete(db_inventory)
    db.commit()
    return db_inventory


# ============================================================================
# Payment CRUD Operations
# ============================================================================

def get_payment(db: Session, payment_id: int) -> Optional[models.Payment]:
    """
    Retrieves a payment by its ID.

    Args:
        db: The database session.
        payment_id: The ID of the payment to fetch.

    Returns:
        The Payment model instance, or None if not found.
    """
    return db.query(models.Payment).filter(models.Payment.id == payment_id).first()


def get_payment_by_transaction(
    db: Session,
    transaction_id: str
) -> Optional[models.Payment]:
    """
    Retrieves a payment by transaction ID.

    Args:
        db: The database session.
        transaction_id: The transaction ID to search for.

    Returns:
        The Payment model instance, or None if not found.
    """
    return db.query(models.Payment).filter(
        models.Payment.transaction_id == transaction_id
    ).first()


def get_payments(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    order_id: Optional[int] = None,
    payment_status: Optional[str] = None
) -> List[models.Payment]:
    """
    Retrieves a list of payments with optional filtering.

    Args:
        db: The database session.
        skip: Number of records to skip (for pagination).
        limit: Maximum number of records to return.
        order_id: Optional order ID to filter by.
        payment_status: Optional payment status to filter by.

    Returns:
        A list of Payment model instances.
    """
    query = db.query(models.Payment)

    if order_id is not None:
        query = query.filter(models.Payment.order_id == order_id)

    if payment_status is not None:
        query = query.filter(models.Payment.payment_status == payment_status)

    return query.order_by(models.Payment.created_at.desc()).offset(skip).limit(limit).all()


def create_payment(
    db: Session,
    payment: schemas.PaymentCreate
) -> models.Payment:
    """
    Creates a new payment record.

    Args:
        db: The database session.
        payment: The Pydantic schema containing the payment data.

    Returns:
        The newly created Payment model instance.
    """
    db_payment = models.Payment(
        order_id=payment.order_id,
        transaction_id=payment.transaction_id,
        payment_status=payment.payment_status,
        amount_paid=payment.amount_paid,
        payment_date=datetime.now() if payment.payment_status == "completed" else None
    )
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment


def update_payment(
    db: Session,
    payment_id: int,
    payment_update: schemas.PaymentUpdate
) -> Optional[models.Payment]:
    """
    Updates an existing payment.

    Args:
        db: The database session.
        payment_id: The ID of the payment to update.
        payment_update: A Pydantic schema with the fields to update.

    Returns:
        The updated Payment model instance, or None if not found.
    """
    db_payment = get_payment(db, payment_id)
    if not db_payment:
        return None

    update_data = payment_update.dict(exclude_unset=True)

    # Auto-set payment_date when status changes to completed
    if "payment_status" in update_data and update_data["payment_status"] == "completed":
        if not db_payment.payment_date:
            update_data["payment_date"] = datetime.now()

    for key, value in update_data.items():
        setattr(db_payment, key, value)

    db.commit()
    db.refresh(db_payment)
    return db_payment


def delete_payment(db: Session, payment_id: int) -> Optional[models.Payment]:
    """
    Deletes a payment from the database.

    Args:
        db: The database session.
        payment_id: The ID of the payment to delete.

    Returns:
        The deleted Payment model instance, or None if not found.
    """
    db_payment = get_payment(db, payment_id)
    if not db_payment:
        return None
    db.delete(db_payment)
    db.commit()
    return db_payment


# ============================================================================
# Order Tracking CRUD Operations
# ============================================================================

def get_order_tracking(
    db: Session,
    tracking_id: int
) -> Optional[models.OrderTracking]:
    """
    Retrieves an order tracking entry by its ID.

    Args:
        db: The database session.
        tracking_id: The ID of the tracking entry to fetch.

    Returns:
        The OrderTracking model instance, or None if not found.
    """
    return db.query(models.OrderTracking).filter(
        models.OrderTracking.id == tracking_id
    ).first()


def get_order_tracking_history(
    db: Session,
    order_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[models.OrderTracking]:
    """
    Retrieves tracking history for a specific order.

    Args:
        db: The database session.
        order_id: The ID of the order.
        skip: Number of records to skip (for pagination).
        limit: Maximum number of records to return.

    Returns:
        A list of OrderTracking model instances.
    """
    return db.query(models.OrderTracking).filter(
        models.OrderTracking.order_id == order_id
    ).order_by(models.OrderTracking.timestamp.desc()).offset(skip).limit(limit).all()


def get_all_tracking_entries(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None
) -> List[models.OrderTracking]:
    """
    Retrieves all tracking entries with optional filtering.

    Args:
        db: The database session.
        skip: Number of records to skip (for pagination).
        limit: Maximum number of records to return.
        status: Optional status to filter by.

    Returns:
        A list of OrderTracking model instances.
    """
    query = db.query(models.OrderTracking)

    if status is not None:
        query = query.filter(models.OrderTracking.status == status)

    return query.order_by(models.OrderTracking.timestamp.desc()).offset(skip).limit(limit).all()


def create_order_tracking(
    db: Session,
    tracking: schemas.OrderTrackingCreate
) -> models.OrderTracking:
    """
    Creates a new order tracking entry.

    Args:
        db: The database session.
        tracking: The Pydantic schema containing the tracking data.

    Returns:
        The newly created OrderTracking model instance.
    """
    db_tracking = models.OrderTracking(
        order_id=tracking.order_id,
        status=tracking.status,
        location=tracking.location,
        notes=tracking.notes
    )
    db.add(db_tracking)
    db.commit()
    db.refresh(db_tracking)
    return db_tracking


def update_order_tracking(
    db: Session,
    tracking_id: int,
    tracking_update: schemas.OrderTrackingUpdate
) -> Optional[models.OrderTracking]:
    """
    Updates an existing order tracking entry.

    Args:
        db: The database session.
        tracking_id: The ID of the tracking entry to update.
        tracking_update: A Pydantic schema with the fields to update.

    Returns:
        The updated OrderTracking model instance, or None if not found.
    """
    db_tracking = get_order_tracking(db, tracking_id)
    if not db_tracking:
        return None

    update_data = tracking_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_tracking, key, value)

    db.commit()
    db.refresh(db_tracking)
    return db_tracking


def delete_order_tracking(
    db: Session,
    tracking_id: int
) -> Optional[models.OrderTracking]:
    """
    Deletes an order tracking entry from the database.

    Args:
        db: The database session.
        tracking_id: The ID of the tracking entry to delete.

    Returns:
        The deleted OrderTracking model instance, or None if not found.
    """
    db_tracking = get_order_tracking(db, tracking_id)
    if not db_tracking:
        return None
    db.delete(db_tracking)
    db.commit()
    return db_tracking


def get_latest_tracking_status(
    db: Session,
    order_id: int
) -> Optional[models.OrderTracking]:
    """
    Gets the latest tracking entry for an order.

    Args:
        db: The database session.
        order_id: The ID of the order.

    Returns:
        The most recent OrderTracking model instance, or None if not found.
    """
    return db.query(models.OrderTracking).filter(
        models.OrderTracking.order_id == order_id
    ).order_by(models.OrderTracking.timestamp.desc()).first()