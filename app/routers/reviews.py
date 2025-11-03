"""
Reviews router for managing product reviews.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import crud, models, schemas
from ..database import get_db
from ..dependencies import get_current_active_user

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post(
    "/", response_model=schemas.ReviewResponse, status_code=status.HTTP_201_CREATED
)
def create_review(
    review: schemas.ReviewCreate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Create a new product review for the authenticated user.

    Args:
        review: Review information including product_id, rating, comment.
        current_user: The authenticated user from JWT token.
        db: Database session dependency.

    Returns:
        The created review with all details.

    Raises:
        HTTPException: If product does not exist.
    """
    # Check if product exists
    product = crud.get_product(db, product_id=review.product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {review.product_id} not found",
        )

    return crud.create_review(db=db, user_id=current_user.id, review=review)


@router.get("/", response_model=List[schemas.ReviewResponse])
def get_reviews(
    skip: int = 0,
    limit: int = 100,
    product_id: Optional[int] = None,
    user_id: Optional[int] = None,
    min_rating: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """
    Retrieve a list of reviews with optional filtering.

    Args:
        skip: Number of records to skip (for pagination).
        limit: Maximum number of records to return.
        product_id: Optional product ID to filter by.
        user_id: Optional user ID to filter by.
        min_rating: Optional minimum rating (1-5) to filter by.
        db: Database session dependency.

    Returns:
        A list of reviews.
    """
    # Validate min_rating if provided
    if min_rating is not None and (min_rating < 1 or min_rating > 5):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="min_rating must be between 1 and 5",
        )

    reviews = crud.get_reviews(
        db,
        skip=skip,
        limit=limit,
        product_id=product_id,
        user_id=user_id,
        min_rating=min_rating,
    )
    return reviews


@router.get("/{review_id}", response_model=schemas.ReviewResponse)
def get_review(review_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific review by ID.

    Args:
        review_id: The ID of the review to retrieve.
        db: Database session dependency.

    Returns:
        The review details.

    Raises:
        HTTPException: If review is not found.
    """
    review = crud.get_review(db, review_id=review_id)
    if review is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Review with ID {review_id} not found",
        )
    return review


@router.get("/products/{product_id}/average-rating")
def get_product_average_rating(product_id: int, db: Session = Depends(get_db)):
    """
    Get the average rating for a product.

    Args:
        product_id: The ID of the product.
        db: Database session dependency.

    Returns:
        The average rating and review count.

    Raises:
        HTTPException: If product is not found.
    """
    # Check if product exists
    product = crud.get_product(db, product_id=product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found",
        )

    # Get average rating
    avg_rating = crud.get_product_average_rating(db, product_id=product_id)

    # Get review count
    review_count = len(crud.get_reviews(db, product_id=product_id, limit=10000))

    return {
        "product_id": product_id,
        "average_rating": round(avg_rating, 2) if avg_rating else 0,
        "review_count": review_count,
    }


@router.put("/{review_id}", response_model=schemas.ReviewResponse)
def update_review(
    review_id: int,
    review_update: schemas.ReviewUpdate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Update a review's information.

    Args:
        review_id: The ID of the review to update.
        review_update: The fields to update (rating, comment).
        current_user: The authenticated user from JWT token.
        db: Database session dependency.

    Returns:
        The updated review.

    Raises:
        HTTPException: If review is not found or doesn't belong to user.
    """
    # Get the review first to verify ownership
    review = crud.get_review(db, review_id=review_id)
    if review is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Review with ID {review_id} not found",
        )

    # Verify the review belongs to the current user
    if review.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own reviews",
        )

    updated_review = crud.update_review(
        db, review_id=review_id, review_update=review_update
    )
    return updated_review


@router.delete("/{review_id}", response_model=schemas.ReviewResponse)
def delete_review(
    review_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Delete a review.

    Args:
        review_id: The ID of the review to delete.
        current_user: The authenticated user from JWT token.
        db: Database session dependency.

    Returns:
        The deleted review.

    Raises:
        HTTPException: If review is not found or doesn't belong to user.
    """
    # Get the review first to verify ownership
    review = crud.get_review(db, review_id=review_id)
    if review is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Review with ID {review_id} not found",
        )

    # Verify the review belongs to the current user
    if review.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own reviews",
        )

    deleted_review = crud.delete_review(db, review_id=review_id)
    return deleted_review
