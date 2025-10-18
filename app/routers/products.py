"""
Product management router for CRUD operations on products.
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db

router = APIRouter(
    prefix="/products",
    tags=["products"]
)


@router.post("/", response_model=schemas.ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product: schemas.ProductCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new product.
    
    Args:
        product: Product information including SKU, name, price, quantity, and description.
        db: Database session dependency.
    
    Returns:
        The created product with all details.
    
    Raises:
        HTTPException: If SKU already exists.
    """
    # Check if SKU already exists
    existing_product = crud.get_product_by_sku(db, sku=product.sku)
    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product with SKU '{product.sku}' already exists"
        )
    
    return crud.create_product(db=db, product=product)


@router.get("/", response_model=List[schemas.ProductResponse])
def get_products(
    skip: int = 0,
    limit: int = 100,
    name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get a list of products with optional filtering and pagination.
    
    Args:
        skip: Number of records to skip (for pagination).
        limit: Maximum number of records to return.
        name: Optional product name filter (case-insensitive partial match).
        db: Database session dependency.
    
    Returns:
        List of products matching the criteria.
    """
    products = crud.get_products(db, skip=skip, limit=limit, name=name)
    return products


@router.get("/{product_id}", response_model=schemas.ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a single product by ID.
    
    Args:
        product_id: The ID of the product to retrieve.
        db: Database session dependency.
    
    Returns:
        The product details.
    
    Raises:
        HTTPException: If product not found.
    """
    db_product = crud.get_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )
    return db_product


@router.get("/sku/{sku}", response_model=schemas.ProductResponse)
def get_product_by_sku(
    sku: str,
    db: Session = Depends(get_db)
):
    """
    Get a single product by SKU.
    
    Args:
        sku: The SKU of the product to retrieve.
        db: Database session dependency.
    
    Returns:
        The product details.
    
    Raises:
        HTTPException: If product not found.
    """
    db_product = crud.get_product_by_sku(db, sku=sku)
    if db_product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with SKU '{sku}' not found"
        )
    return db_product


@router.put("/{product_id}", response_model=schemas.ProductResponse)
def update_product(
    product_id: int,
    product: schemas.ProductUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing product.
    
    Args:
        product_id: The ID of the product to update.
        product: Product fields to update (only provided fields will be updated).
        db: Database session dependency.
    
    Returns:
        The updated product details.
    
    Raises:
        HTTPException: If product not found.
    """
    db_product = crud.update_product(db, product_id=product_id, product_update=product)
    if db_product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )
    return db_product


@router.delete("/{product_id}", response_model=schemas.ProductResponse)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a product.
    
    Args:
        product_id: The ID of the product to delete.
        db: Database session dependency.
    
    Returns:
        The deleted product details.
    
    Raises:
        HTTPException: If product not found.
    """
    db_product = crud.delete_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )
    return db_product

