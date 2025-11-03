"""
Superadmin router for administrative operations.

Provides endpoints for:
- Product management (create, update, delete, pricing)
- User management (list, delete, update roles)
- Review moderation (show/hide reviews)

All endpoints require superadmin access.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import crud, models, schemas
from ..database import get_db
from ..dependencies import require_superadmin

router = APIRouter(
    prefix="/superadmin",
    tags=["superadmin"],
    dependencies=[Depends(require_superadmin)],
)


# ============================================================================
# PRODUCT MANAGEMENT ENDPOINTS
# ============================================================================


@router.post(
    "/products",
    response_model=schemas.ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_product(
    product: schemas.SuperadminProductCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_superadmin),
):
    """
    Create a new product (superadmin only).

    Args:
        product: Product creation data.
        db: Database session dependency.
        current_user: The authenticated superadmin user.

    Returns:
        The created product.

    Raises:
        HTTPException: If SKU already exists.
    """
    # Check if SKU already exists
    existing_product = crud.get_product_by_sku(db, sku=product.sku)
    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product with SKU '{product.sku}' already exists",
        )

    # Create the product
    db_product = crud.create_product(db=db, product=product)
    return db_product


@router.put("/products/{product_id}", response_model=schemas.ProductResponse)
def update_product(
    product_id: int,
    product_update: schemas.SuperadminProductUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_superadmin),
):
    """
    Update a product (superadmin only).

    Args:
        product_id: The ID of the product to update.
        product_update: Product update data.
        db: Database session dependency.
        current_user: The authenticated superadmin user.

    Returns:
        The updated product.

    Raises:
        HTTPException: If product not found or SKU conflict.
    """
    # Check if product exists
    db_product = crud.get_product(db, product_id=product_id)
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    # If updating SKU, check for conflicts
    if product_update.sku and product_update.sku != db_product.sku:
        existing_product = crud.get_product_by_sku(db, sku=product_update.sku)
        if existing_product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product with SKU '{product_update.sku}' already exists",
            )

    # Update the product
    updated_product = crud.update_product(
        db=db, product_id=product_id, product_update=product_update
    )
    return updated_product


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_superadmin),
):
    """
    Delete a product (superadmin only).

    Args:
        product_id: The ID of the product to delete.
        db: Database session dependency.
        current_user: The authenticated superadmin user.

    Raises:
        HTTPException: If product not found.
    """
    db_product = crud.delete_product(db, product_id=product_id)
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )
    return None


@router.patch("/products/{product_id}/price", response_model=schemas.ProductResponse)
def update_product_price(
    product_id: int,
    price: float,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_superadmin),
):
    """
    Update product pricing (superadmin only).

    Args:
        product_id: The ID of the product to update.
        price: The new price for the product.
        db: Database session dependency.
        current_user: The authenticated superadmin user.

    Returns:
        The updated product.

    Raises:
        HTTPException: If product not found or price is invalid.
    """
    if price < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Price cannot be negative"
        )

    # Update using the existing update function
    product_update = schemas.ProductUpdate(price=price)
    updated_product = crud.update_product(
        db=db, product_id=product_id, product_update=product_update
    )

    if not updated_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    return updated_product


# ============================================================================
# USER MANAGEMENT ENDPOINTS
# ============================================================================


@router.get("/users", response_model=List[schemas.UserResponse])
def list_all_users(
    skip: int = 0,
    limit: int = 100,
    username: Optional[str] = None,
    role: Optional[schemas.UserRoleEnum] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_superadmin),
):
    """
    List all users with optional filtering (superadmin only).

    Args:
        skip: Number of records to skip for pagination.
        limit: Maximum number of records to return.
        username: Optional username filter.
        role: Optional role filter.
        db: Database session dependency.
        current_user: The authenticated superadmin user.

    Returns:
        List of users.
    """
    # Convert schema enum to model enum if provided
    model_role = None
    if role:
        model_role = models.UserRole(role.value)

    users = crud.get_users(
        db=db, skip=skip, limit=limit, username=username, role=model_role
    )
    return users


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_superadmin),
):
    """
    Delete a user (superadmin only).

    Args:
        user_id: The ID of the user to delete.
        db: Database session dependency.
        current_user: The authenticated superadmin user.

    Raises:
        HTTPException: If user not found or trying to delete self.
    """
    # Prevent superadmin from deleting themselves
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account",
        )

    db_user = crud.delete_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return None


@router.patch("/users/{user_id}/role", response_model=schemas.UserResponse)
def update_user_role(
    user_id: int,
    role_update: schemas.UserRoleUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_superadmin),
):
    """
    Update a user's role (superadmin only).

    Args:
        user_id: The ID of the user to update.
        role_update: The new role information.
        db: Database session dependency.
        current_user: The authenticated superadmin user.

    Returns:
        The updated user.

    Raises:
        HTTPException: If user not found or trying to modify self.
    """
    # Prevent superadmin from modifying their own role
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify your own role",
        )

    # Convert schema enum to model enum
    model_role = models.UserRole(role_update.role.value)

    # Update the user's role
    updated_user = crud.update_user_role(
        db=db, user_id=user_id, role=model_role, is_superadmin=role_update.is_superadmin
    )

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return updated_user


# ============================================================================
# REVIEW MODERATION ENDPOINTS
# ============================================================================


@router.patch("/reviews/{review_id}/visibility", response_model=schemas.ReviewResponse)
def moderate_review(
    review_id: int,
    moderation: schemas.ReviewModerationUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_superadmin),
):
    """
    Show or hide a review (superadmin only).

    Args:
        review_id: The ID of the review to moderate.
        moderation: The moderation action (show/hide).
        db: Database session dependency.
        current_user: The authenticated superadmin user.

    Returns:
        The moderated review.

    Raises:
        HTTPException: If review not found.
    """
    moderated_review = crud.moderate_review(
        db=db, review_id=review_id, is_visible=moderation.is_visible
    )

    if not moderated_review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Review not found"
        )

    return moderated_review
