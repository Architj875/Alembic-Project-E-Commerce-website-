"""
Orders router for managing customer orders.
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import crud, models, schemas
from ..database import get_db
from ..dependencies import get_current_active_user

router = APIRouter(
    prefix="/orders",
    tags=["orders"]
)


@router.post(
    "/",
    response_model=schemas.OrderResponse,
    status_code=status.HTTP_201_CREATED
)
def create_order(
    order: schemas.OrderCreate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new order from the authenticated user's shopping cart.

    Args:
        order: Order information including cart_id and address.
        current_user: The authenticated user from JWT token.
        db: Database session dependency.

    Returns:
        The created order with all details.

    Raises:
        HTTPException: If cart does not exist, doesn't belong to user, or cart is empty.
    """
    # Check if cart exists
    cart = crud.get_shopping_cart(db, cart_id=order.cart_id)
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cart with ID {order.cart_id} not found"
        )

    # Check if cart belongs to current user
    if cart.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create orders from your own cart"
        )

    # Check if cart has items
    if not cart.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create order from empty cart"
        )

    # Check stock availability for all items
    for item in cart.items:
        product = crud.get_product(db, product_id=item.product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {item.product_id} not found"
            )
        if product.quantity < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for {product.name}. Available: {product.quantity}"
            )

    # Create order for current user
    db_order = crud.create_order(db=db, customer_id=current_user.id, order=order)

    # Update product quantities
    for item in cart.items:
        product = crud.get_product(db, product_id=item.product_id)
        if product:
            product.quantity -= item.quantity
            db.commit()

    return db_order


@router.get("/", response_model=List[schemas.OrderResponse])
def get_orders(
    skip: int = 0,
    limit: int = 100,
    order_status: Optional[str] = None,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of orders for the authenticated user with optional filtering.

    Args:
        skip: Number of records to skip (for pagination).
        limit: Maximum number of records to return.
        order_status: Optional order status to filter by.
        current_user: The authenticated user from JWT token.
        db: Database session dependency.

    Returns:
        A list of the user's orders.
    """
    # Only return orders for the current user
    orders = crud.get_orders(
        db,
        skip=skip,
        limit=limit,
        customer_id=current_user.id,
        order_status=order_status
    )
    return orders


@router.get("/{order_id}", response_model=schemas.OrderResponse)
def get_order(
    order_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific order by ID.

    Args:
        order_id: The ID of the order to retrieve.
        current_user: The authenticated user from JWT token.
        db: Database session dependency.

    Returns:
        The order details.

    Raises:
        HTTPException: If order is not found or doesn't belong to user.
    """
    order = crud.get_order(db, order_id=order_id)
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} not found"
        )

    # Verify the order belongs to the current user
    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own orders"
        )

    return order


@router.put("/{order_id}", response_model=schemas.OrderResponse)
def update_order(
    order_id: int,
    order_update: schemas.OrderUpdate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update an order's information.

    Args:
        order_id: The ID of the order to update.
        order_update: The fields to update (address, order_status).
        current_user: The authenticated user from JWT token.
        db: Database session dependency.

    Returns:
        The updated order.

    Raises:
        HTTPException: If order is not found, doesn't belong to user, or invalid status.
    """
    # Get the order first to verify ownership
    order = crud.get_order(db, order_id=order_id)
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} not found"
        )

    # Verify the order belongs to the current user
    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own orders"
        )

    # Validate order status if provided
    valid_statuses = ["pending", "confirmed", "shipped", "delivered", "cancelled"]
    if order_update.order_status and order_update.order_status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid order status. Must be one of: {', '.join(valid_statuses)}"
        )

    updated_order = crud.update_order(db, order_id=order_id, order_update=order_update)
    return updated_order


@router.delete("/{order_id}", response_model=schemas.OrderResponse)
def delete_order(
    order_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete an order.

    Args:
        order_id: The ID of the order to delete.
        current_user: The authenticated user from JWT token.
        db: Database session dependency.

    Returns:
        The deleted order.

    Raises:
        HTTPException: If order is not found, doesn't belong to user, or cannot be deleted.
    """
    # Get order first to check status and ownership
    order = crud.get_order(db, order_id=order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} not found"
        )

    # Verify the order belongs to the current user
    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own orders"
        )

    # Don't allow deletion of shipped or delivered orders
    if order.order_status in ["shipped", "delivered"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete order with status '{order.order_status}'"
        )

    deleted_order = crud.delete_order(db, order_id=order_id)
    return deleted_order

