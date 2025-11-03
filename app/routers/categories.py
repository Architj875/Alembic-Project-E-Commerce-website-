"""
Product Categories router for managing product categories.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import crud, models, schemas
from ..dependencies import require_admin
from ..database import get_db

router = APIRouter(prefix="/categories", tags=["product-categories"])


@router.post(
    "/",
    response_model=schemas.ProductCategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_category(
    category: schemas.ProductCategoryCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    """
    Create a new product category.

    Args:
        category: Category information including product_id, category_id, name.
        db: Database session dependency.

    Returns:
        The created product category with all details.

    Raises:
        HTTPException: If product does not exist.
    """
    # Check if product exists
    product = crud.get_product(db, product_id=category.product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {category.product_id} not found",
        )

    return crud.create_product_category(db=db, category=category)


@router.get("/", response_model=List[schemas.ProductCategoryResponse])
def get_categories(
    skip: int = 0,
    limit: int = 100,
    product_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    """
    Retrieve a list of product categories with optional filtering.

    Args:
        skip: Number of records to skip (for pagination).
        limit: Maximum number of records to return.
        product_id: Optional product ID to filter by.
        is_active: Optional active status to filter by.
        db: Database session dependency.

    Returns:
        A list of product categories.
    """
    categories = crud.get_product_categories(
        db, skip=skip, limit=limit, product_id=product_id, is_active=is_active
    )
    return categories


@router.get("/{category_id}", response_model=schemas.ProductCategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific product category by ID.

    Args:
        category_id: The ID of the category to retrieve.
        db: Database session dependency.

    Returns:
        The product category details.

    Raises:
        HTTPException: If category is not found.
    """
    category = crud.get_product_category(db, category_id=category_id)
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found",
        )
    return category


@router.put("/{category_id}", response_model=schemas.ProductCategoryResponse)
def update_category(
    category_id: int,
    category_update: schemas.ProductCategoryUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    """
    Update a product category's information.

    Args:
        category_id: The ID of the category to update.
        category_update: The fields to update.
        db: Database session dependency.

    Returns:
        The updated product category.

    Raises:
        HTTPException: If category is not found.
    """
    category = crud.update_product_category(
        db, category_id=category_id, category_update=category_update
    )
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found",
        )
    return category


@router.delete("/{category_id}", response_model=schemas.ProductCategoryResponse)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    """
    Delete a product category.

    Args:
        category_id: The ID of the category to delete.
        db: Database session dependency.

    Returns:
        The deleted product category.

    Raises:
        HTTPException: If category is not found.
    """
    category = crud.delete_product_category(db, category_id=category_id)
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found",
        )
    return category
