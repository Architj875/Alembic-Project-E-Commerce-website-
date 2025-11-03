"""
Addresses router for managing customer addresses.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import crud, models, schemas
from ..database import get_db
from ..dependencies import get_current_active_user

router = APIRouter(prefix="/addresses", tags=["addresses"])


@router.post(
    "/", response_model=schemas.AddressResponse, status_code=status.HTTP_201_CREATED
)
def create_address(
    address: schemas.AddressCreate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Create a new address for the authenticated user.

    Args:
        address: Address information including street, city, state, country.
        current_user: The authenticated user from JWT token.
        db: Database session dependency.

    Returns:
        The created address with all details.
    """
    return crud.create_address(db=db, user_id=current_user.id, address=address)


@router.get("/", response_model=List[schemas.AddressResponse])
def get_addresses(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve a list of addresses for the authenticated user.

    Args:
        skip: Number of records to skip (for pagination).
        limit: Maximum number of records to return.
        current_user: The authenticated user from JWT token.
        db: Database session dependency.

    Returns:
        A list of the user's addresses.
    """
    # Only return addresses for the current user
    addresses = crud.get_addresses(db, skip=skip, limit=limit, user_id=current_user.id)
    return addresses


@router.get("/{address_id}", response_model=schemas.AddressResponse)
def get_address(
    address_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve a specific address by ID.

    Args:
        address_id: The ID of the address to retrieve.
        current_user: The authenticated user from JWT token.
        db: Database session dependency.

    Returns:
        The address details.

    Raises:
        HTTPException: If address is not found or doesn't belong to user.
    """
    address = crud.get_address(db, address_id=address_id)
    if address is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Address with ID {address_id} not found",
        )

    # Verify the address belongs to the current user
    if address.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own addresses",
        )

    return address


@router.put("/{address_id}", response_model=schemas.AddressResponse)
def update_address(
    address_id: int,
    address_update: schemas.AddressUpdate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Update an address's information.

    Args:
        address_id: The ID of the address to update.
        address_update: The fields to update.
        current_user: The authenticated user from JWT token.
        db: Database session dependency.

    Returns:
        The updated address.

    Raises:
        HTTPException: If address is not found or doesn't belong to user.
    """
    # Get the address first to verify ownership
    address = crud.get_address(db, address_id=address_id)
    if address is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Address with ID {address_id} not found",
        )

    # Verify the address belongs to the current user
    if address.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own addresses",
        )

    updated_address = crud.update_address(
        db, address_id=address_id, address_update=address_update
    )
    return updated_address


@router.delete("/{address_id}", response_model=schemas.AddressResponse)
def delete_address(
    address_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Delete an address.

    Args:
        address_id: The ID of the address to delete.
        current_user: The authenticated user from JWT token.
        db: Database session dependency.

    Returns:
        The deleted address.

    Raises:
        HTTPException: If address is not found or doesn't belong to user.
    """
    # Get the address first to verify ownership
    address = crud.get_address(db, address_id=address_id)
    if address is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Address with ID {address_id} not found",
        )

    # Verify the address belongs to the current user
    if address.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own addresses",
        )

    deleted_address = crud.delete_address(db, address_id=address_id)
    return deleted_address
