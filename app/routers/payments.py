"""
Payments router for managing order payments.
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import crud, models, schemas
from ..database import get_db
from ..dependencies import get_current_active_user

router = APIRouter(
    prefix="/payments",
    tags=["payments"]
)


@router.post(
    "/",
    response_model=schemas.PaymentResponse,
    status_code=status.HTTP_201_CREATED
)
def create_payment(
    payment: schemas.PaymentCreate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new payment for an order.

    Args:
        payment: Payment information including order_id, transaction_id, amount.
        current_user: The authenticated user from JWT token.
        db: Database session dependency.

    Returns:
        The created payment with all details.

    Raises:
        HTTPException: If order does not exist, doesn't belong to user, or transaction_id already exists.
    """
    # Check if order exists
    order = crud.get_order(db, order_id=payment.order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {payment.order_id} not found"
        )

    # Verify the order belongs to the current user
    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create payments for your own orders"
        )

    # Check if transaction_id already exists
    existing_payment = crud.get_payment_by_transaction(
        db,
        transaction_id=payment.transaction_id
    )
    if existing_payment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment with transaction ID {payment.transaction_id} already exists"
        )

    return crud.create_payment(db=db, payment=payment)


@router.get("/", response_model=List[schemas.PaymentResponse])
def get_payments(
    skip: int = 0,
    limit: int = 100,
    order_id: Optional[int] = None,
    payment_status: Optional[str] = None,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of payments for the authenticated user's orders.

    Args:
        skip: Number of records to skip (for pagination).
        limit: Maximum number of records to return.
        order_id: Optional order ID to filter by (must belong to user).
        payment_status: Optional payment status to filter by.
        current_user: The authenticated user from JWT token.
        db: Database session dependency.

    Returns:
        A list of the user's payments.

    Raises:
        HTTPException: If order_id is provided but doesn't belong to user.
    """
    # If order_id is provided, verify it belongs to the current user
    if order_id:
        order = crud.get_order(db, order_id=order_id)
        if not order or order.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view payments for your own orders"
            )

    # Get all payments for user's orders
    payments = crud.get_payments(
        db,
        skip=skip,
        limit=limit,
        order_id=order_id,
        payment_status=payment_status
    )

    # Filter to only include payments for user's orders
    user_payments = [p for p in payments if crud.get_order(db, p.order_id).user_id == current_user.id]

    return user_payments


@router.get("/{payment_id}", response_model=schemas.PaymentResponse)
def get_payment(
    payment_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific payment by ID.

    Args:
        payment_id: The ID of the payment to retrieve.
        current_user: The authenticated user from JWT token.
        db: Database session dependency.

    Returns:
        The payment details.

    Raises:
        HTTPException: If payment is not found or doesn't belong to user's order.
    """
    payment = crud.get_payment(db, payment_id=payment_id)
    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment with ID {payment_id} not found"
        )

    # Verify the payment's order belongs to the current user
    order = crud.get_order(db, order_id=payment.order_id)
    if not order or order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view payments for your own orders"
        )

    return payment


@router.get("/transaction/{transaction_id}", response_model=schemas.PaymentResponse)
def get_payment_by_transaction(
    transaction_id: str,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve a payment by transaction ID.

    Args:
        transaction_id: The transaction ID to search for.
        current_user: The authenticated user from JWT token.
        db: Database session dependency.

    Returns:
        The payment details.

    Raises:
        HTTPException: If payment is not found or doesn't belong to user's order.
    """
    payment = crud.get_payment_by_transaction(db, transaction_id=transaction_id)
    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment with transaction ID {transaction_id} not found"
        )

    # Verify the payment's order belongs to the current user
    order = crud.get_order(db, order_id=payment.order_id)
    if not order or order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view payments for your own orders"
        )

    return payment


@router.put("/{payment_id}", response_model=schemas.PaymentResponse)
def update_payment(
    payment_id: int,
    payment_update: schemas.PaymentUpdate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update a payment's information.

    Args:
        payment_id: The ID of the payment to update.
        payment_update: The fields to update (payment_status, payment_date).
        current_user: The authenticated user from JWT token.
        db: Database session dependency.

    Returns:
        The updated payment.

    Raises:
        HTTPException: If payment is not found or doesn't belong to user's order.
    """
    # Get the payment first to verify ownership
    payment = crud.get_payment(db, payment_id=payment_id)
    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment with ID {payment_id} not found"
        )

    # Verify the payment's order belongs to the current user
    order = crud.get_order(db, order_id=payment.order_id)
    if not order or order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update payments for your own orders"
        )

    updated_payment = crud.update_payment(
        db,
        payment_id=payment_id,
        payment_update=payment_update
    )
    return updated_payment


@router.delete("/{payment_id}", response_model=schemas.PaymentResponse)
def delete_payment(
    payment_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a payment.

    Args:
        payment_id: The ID of the payment to delete.
        current_user: The authenticated user from JWT token.
        db: Database session dependency.

    Returns:
        The deleted payment.

    Raises:
        HTTPException: If payment is not found or doesn't belong to user's order.
    """
    # Get the payment first to verify ownership
    payment = crud.get_payment(db, payment_id=payment_id)
    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment with ID {payment_id} not found"
        )

    # Verify the payment's order belongs to the current user
    order = crud.get_order(db, order_id=payment.order_id)
    if not order or order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete payments for your own orders"
        )

    deleted_payment = crud.delete_payment(db, payment_id=payment_id)
    return deleted_payment

