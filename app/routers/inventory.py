"""
Inventory router for managing product inventory.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import crud, models, schemas
from ..database import get_db

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"]
)


@router.post(
    "/",
    response_model=schemas.InventoryResponse,
    status_code=status.HTTP_201_CREATED
)
def create_inventory(
    inventory: schemas.InventoryCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new inventory record for a product.

    Args:
        inventory: Inventory information including product_id, quantity, reorder_level.
        db: Database session dependency.

    Returns:
        The created inventory record with all details.

    Raises:
        HTTPException: If product does not exist or already has inventory.
    """
    # Check if product exists
    product = crud.get_product(db, product_id=inventory.product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {inventory.product_id} not found"
        )

    # Check if inventory already exists for this product
    existing_inventory = crud.get_inventory_by_product(db, product_id=inventory.product_id)
    if existing_inventory:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Inventory already exists for product {inventory.product_id}"
        )

    return crud.create_inventory(db=db, inventory=inventory)


@router.get("/", response_model=List[schemas.InventoryResponse])
def get_inventories(
    skip: int = 0,
    limit: int = 100,
    low_stock_only: bool = False,
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of inventory records with optional filtering.

    Args:
        skip: Number of records to skip (for pagination).
        limit: Maximum number of records to return.
        low_stock_only: If True, only return items at or below reorder level.
        db: Database session dependency.

    Returns:
        A list of inventory records.
    """
    inventories = crud.get_inventories(
        db,
        skip=skip,
        limit=limit,
        low_stock_only=low_stock_only
    )
    return inventories


@router.get("/{inventory_id}", response_model=schemas.InventoryResponse)
def get_inventory(inventory_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific inventory record by ID.

    Args:
        inventory_id: The ID of the inventory record to retrieve.
        db: Database session dependency.

    Returns:
        The inventory record details.

    Raises:
        HTTPException: If inventory record is not found.
    """
    inventory = crud.get_inventory(db, inventory_id=inventory_id)
    if inventory is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inventory with ID {inventory_id} not found"
        )
    return inventory


@router.get("/products/{product_id}", response_model=schemas.InventoryResponse)
def get_inventory_by_product(product_id: int, db: Session = Depends(get_db)):
    """
    Retrieve inventory record for a specific product.

    Args:
        product_id: The ID of the product.
        db: Database session dependency.

    Returns:
        The inventory record for the product.

    Raises:
        HTTPException: If product or inventory is not found.
    """
    # Check if product exists
    product = crud.get_product(db, product_id=product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )

    inventory = crud.get_inventory_by_product(db, product_id=product_id)
    if inventory is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inventory not found for product {product_id}"
        )
    return inventory


@router.put("/{inventory_id}", response_model=schemas.InventoryResponse)
def update_inventory(
    inventory_id: int,
    inventory_update: schemas.InventoryUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an inventory record's information.

    Args:
        inventory_id: The ID of the inventory record to update.
        inventory_update: The fields to update (quantity_in_stock, reorder_level).
        db: Database session dependency.

    Returns:
        The updated inventory record.

    Raises:
        HTTPException: If inventory record is not found.
    """
    inventory = crud.update_inventory(
        db,
        inventory_id=inventory_id,
        inventory_update=inventory_update
    )
    if inventory is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inventory with ID {inventory_id} not found"
        )
    return inventory


@router.post("/{inventory_id}/restock", response_model=schemas.InventoryResponse)
def restock_inventory(
    inventory_id: int,
    restock: schemas.InventoryRestock,
    db: Session = Depends(get_db)
):
    """
    Restock inventory by adding quantity.

    Args:
        inventory_id: The ID of the inventory record to restock.
        restock: The quantity to add to stock.
        db: Database session dependency.

    Returns:
        The updated inventory record with new stock level.

    Raises:
        HTTPException: If inventory record is not found.
    """
    inventory = crud.restock_inventory(
        db,
        inventory_id=inventory_id,
        quantity_to_add=restock.quantity_to_add
    )
    if inventory is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inventory with ID {inventory_id} not found"
        )
    return inventory


@router.delete("/{inventory_id}", response_model=schemas.InventoryResponse)
def delete_inventory(inventory_id: int, db: Session = Depends(get_db)):
    """
    Delete an inventory record.

    Args:
        inventory_id: The ID of the inventory record to delete.
        db: Database session dependency.

    Returns:
        The deleted inventory record.

    Raises:
        HTTPException: If inventory record is not found.
    """
    inventory = crud.delete_inventory(db, inventory_id=inventory_id)
    if inventory is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inventory with ID {inventory_id} not found"
        )
    return inventory

