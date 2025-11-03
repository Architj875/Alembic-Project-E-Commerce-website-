"""
Shopping Cart router for managing customer shopping carts.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import crud, models, schemas
from ..database import get_db
from ..dependencies import get_current_active_user

router = APIRouter(
    prefix="/cart",
    tags=["shopping-cart"]
)


@router.get(
    "/",
    response_model=schemas.ShoppingCartResponse
)
def get_cart(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get the shopping cart for the authenticated user.

    Args:
        current_user: The authenticated user from JWT token.
        db: Database session dependency.

    Returns:
        The user's shopping cart with all items.
    """
    # Get or create cart for current user
    cart = crud.get_customer_cart(db, user_id=current_user.id)
    if not cart:
        cart = crud.create_shopping_cart(db, user_id=current_user.id)

    return cart


@router.post(
    "/items",
    response_model=schemas.ShoppingCartItemResponse,
    status_code=status.HTTP_201_CREATED
)
def add_item(
    item: schemas.ShoppingCartItemCreate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Add an item to the authenticated user's shopping cart.

    Args:
        item: Item information including product_id and quantity.
        current_user: The authenticated user from JWT token.
        db: Database session dependency.

    Returns:
        The added cart item.

    Raises:
        HTTPException: If product does not exist or insufficient stock.
    """
    # Check if product exists
    product = crud.get_product(db, product_id=item.product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {item.product_id} not found"
        )

    # Check inventory for stock (Inventory is canonical)
    inventory = crud.get_inventory_by_product(db, product_id=item.product_id)
    if not inventory or inventory.quantity_in_stock < item.quantity:
        available = inventory.quantity_in_stock if inventory else 0
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient stock. Available: {available}"
        )

    # Get or create cart for current user
    cart = crud.get_customer_cart(db, user_id=current_user.id)
    if not cart:
        cart = crud.create_shopping_cart(db, user_id=current_user.id)

    # Add item to cart
    cart_item = crud.add_item_to_cart(db, cart_id=cart.id, item=item)
    return cart_item


@router.put(
    "/items/{item_id}",
    response_model=schemas.ShoppingCartItemResponse
)
def update_item(
    item_id: int,
    item_update: schemas.ShoppingCartItemUpdate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update the quantity of a cart item.

    Args:
        item_id: The ID of the cart item to update.
        item_update: The new quantity.
        current_user: The authenticated user from JWT token.
        db: Database session dependency.

    Returns:
        The updated cart item.

    Raises:
        HTTPException: If item is not found, doesn't belong to user, or insufficient stock.
    """
    # Get the cart item
    cart_item = db.query(models.ShoppingCartItem).filter(
        models.ShoppingCartItem.id == item_id
    ).first()

    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cart item with ID {item_id} not found"
        )

    # Verify the cart item belongs to the current user
    cart = crud.get_shopping_cart(db, cart_id=cart_item.cart_id)
    if not cart or cart.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update items in your own cart"
        )

    # Check product inventory for stock
    inventory = crud.get_inventory_by_product(db, product_id=cart_item.product_id)
    if not inventory or inventory.quantity_in_stock < item_update.quantity:
        available = inventory.quantity_in_stock if inventory else 0
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient stock. Available: {available}"
        )

    # Update item
    updated_item = crud.update_cart_item(db, item_id=item_id, item_update=item_update)
    return updated_item


@router.delete(
    "/items/{item_id}",
    response_model=schemas.ShoppingCartItemResponse
)
def remove_item(
    item_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Remove an item from the authenticated user's shopping cart.

    Args:
        item_id: The ID of the cart item to remove.
        current_user: The authenticated user from JWT token.
        db: Database session dependency.

    Returns:
        The removed cart item.

    Raises:
        HTTPException: If item is not found or doesn't belong to user.
    """
    # Get the cart item first to verify ownership
    cart_item = db.query(models.ShoppingCartItem).filter(
        models.ShoppingCartItem.id == item_id
    ).first()

    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cart item with ID {item_id} not found"
        )

    # Verify the cart item belongs to the current user
    cart = crud.get_shopping_cart(db, cart_id=cart_item.cart_id)
    if not cart or cart.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only remove items from your own cart"
        )

    # Remove the item
    removed_item = crud.remove_item_from_cart(db, item_id=item_id)
    return removed_item


@router.delete("/clear")
def clear_cart(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Clear all items from the authenticated user's shopping cart.

    Args:
        current_user: The authenticated user from JWT token.
        db: Database session dependency.

    Returns:
        Success message.

    Raises:
        HTTPException: If cart is not found.
    """
    # Get current user's cart
    cart = crud.get_customer_cart(db, user_id=current_user.id)
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found"
        )

    # Clear cart
    crud.clear_cart(db, cart_id=cart.id)
    return {"message": "Cart cleared successfully"}

