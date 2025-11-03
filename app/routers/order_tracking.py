"""
Order Tracking router for managing order tracking information.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import crud, models, schemas
from ..dependencies import require_admin
from ..database import get_db

router = APIRouter(prefix="/order-tracking", tags=["order-tracking"])


@router.post(
    "/",
    response_model=schemas.OrderTrackingResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_tracking_entry(
    tracking: schemas.OrderTrackingCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    """
    Create a new tracking entry for an order.

    Args:
        tracking: Tracking information including order_id, status, location, notes.
        db: Database session dependency.

    Returns:
        The created tracking entry with all details.

    Raises:
        HTTPException: If order does not exist.
    """
    # Check if order exists
    order = crud.get_order(db, order_id=tracking.order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {tracking.order_id} not found",
        )

    return crud.create_order_tracking(db=db, tracking=tracking)


@router.get("/", response_model=List[schemas.OrderTrackingResponse])
def get_all_tracking_entries(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    Retrieve all tracking entries with optional filtering.

    Args:
        skip: Number of records to skip (for pagination).
        limit: Maximum number of records to return.
        status: Optional status to filter by.
        db: Database session dependency.

    Returns:
        A list of tracking entries.
    """
    tracking_entries = crud.get_all_tracking_entries(
        db, skip=skip, limit=limit, status=status
    )
    return tracking_entries


@router.get("/{tracking_id}", response_model=schemas.OrderTrackingResponse)
def get_tracking_entry(tracking_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific tracking entry by ID.

    Args:
        tracking_id: The ID of the tracking entry to retrieve.
        db: Database session dependency.

    Returns:
        The tracking entry details.

    Raises:
        HTTPException: If tracking entry is not found.
    """
    tracking = crud.get_order_tracking(db, tracking_id=tracking_id)
    if tracking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tracking entry with ID {tracking_id} not found",
        )
    return tracking


@router.get("/orders/{order_id}", response_model=List[schemas.OrderTrackingResponse])
def get_order_tracking_history(
    order_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """
    Retrieve tracking history for a specific order.

    Args:
        order_id: The ID of the order.
        skip: Number of records to skip (for pagination).
        limit: Maximum number of records to return.
        db: Database session dependency.

    Returns:
        A list of tracking entries for the order.

    Raises:
        HTTPException: If order is not found.
    """
    # Check if order exists
    order = crud.get_order(db, order_id=order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} not found",
        )

    tracking_history = crud.get_order_tracking_history(
        db, order_id=order_id, skip=skip, limit=limit
    )
    return tracking_history


@router.get("/orders/{order_id}/latest", response_model=schemas.OrderTrackingResponse)
def get_latest_tracking_status(order_id: int, db: Session = Depends(get_db)):
    """
    Get the latest tracking status for an order.

    Args:
        order_id: The ID of the order.
        db: Database session dependency.

    Returns:
        The most recent tracking entry for the order.

    Raises:
        HTTPException: If order is not found or has no tracking entries.
    """
    # Check if order exists
    order = crud.get_order(db, order_id=order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} not found",
        )

    latest_tracking = crud.get_latest_tracking_status(db, order_id=order_id)
    if latest_tracking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No tracking information found for order {order_id}",
        )
    return latest_tracking


@router.put("/{tracking_id}", response_model=schemas.OrderTrackingResponse)
def update_tracking_entry(
    tracking_id: int,
    tracking_update: schemas.OrderTrackingUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    """
    Update a tracking entry's information.

    Args:
        tracking_id: The ID of the tracking entry to update.
        tracking_update: The fields to update (status, location, notes).
        db: Database session dependency.

    Returns:
        The updated tracking entry.

    Raises:
        HTTPException: If tracking entry is not found.
    """
    tracking = crud.update_order_tracking(
        db, tracking_id=tracking_id, tracking_update=tracking_update
    )
    if tracking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tracking entry with ID {tracking_id} not found",
        )
    return tracking


@router.delete("/{tracking_id}", response_model=schemas.OrderTrackingResponse)
def delete_tracking_entry(
    tracking_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    """
    Delete a tracking entry.

    Args:
        tracking_id: The ID of the tracking entry to delete.
        db: Database session dependency.

    Returns:
        The deleted tracking entry.

    Raises:
        HTTPException: If tracking entry is not found.
    """
    tracking = crud.delete_order_tracking(db, tracking_id=tracking_id)
    if tracking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tracking entry with ID {tracking_id} not found",
        )
    return tracking
