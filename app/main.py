from fastapi import FastAPI

from .routers import (
    addresses,
    auth,
    cart,
    categories,
    inventory,
    order_tracking,
    orders,
    payments,
    products,
    reviews,
    superadmin,
)

app = FastAPI(
    title="FastAPI E-Commerce Platform",
    description="E-commerce API with role-based access control",
    version="2.0.0"
)

# Include routers
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(categories.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(addresses.router)
app.include_router(reviews.router)
app.include_router(inventory.router)
app.include_router(payments.router)
app.include_router(order_tracking.router)
app.include_router(superadmin.router)

# Legacy user endpoints - These are now handled by auth router and superadmin router
# Kept here for reference but commented out to avoid conflicts
#
# User signup/login: Use /auth/signup and /auth/login
# User management: Use /superadmin/users/* (requires superadmin access)
#
# @app.post("/users/", response_model=schemas.User)
# def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
#     db_user = crud.get_user_by_email(db, email=user.email)
#     if db_user:
#         raise HTTPException(status_code=400, detail="Email already registered")
#     return crud.create_user(db=db, user=user)
#
# @app.get("/users/", response_model=List[schemas.User])
# def read_users(skip: int = 0, limit: int = 100, name: Optional[str] = None, db: Session = Depends(get_db)):
#     users = crud.get_users(db, skip=skip, limit=limit, name=name)
#     return users
#
# @app.get("/users/{user_id}", response_model=schemas.User)
# def read_user(user_id: int, db: Session = Depends(get_db)):
#     db_user = crud.get_user(db, user_id=user_id)
#     if db_user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return db_user
#
# @app.put("/users/{user_id}", response_model=schemas.User)
# def update_user(user_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db)):
#     db_user = crud.update_user(db, user_id=user_id, user_update=user)
#     if db_user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return db_user
#
# @app.delete("/users/{user_id}", response_model=schemas.User)
# def delete_user(user_id: int, db: Session = Depends(get_db)):
#     db_user = crud.delete_user(db, user_id=user_id)
#     if db_user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return db_user


@app.get("/")
def root():
    """Root endpoint with API information."""
    return {
        "message": "FastAPI E-Commerce Platform",
        "version": "2.0.0",
        "features": [
            "User authentication with JWT",
            "Role-based access control (Customer, Admin, Superadmin)",
            "Product management",
            "Shopping cart",
            "Orders and payments",
            "Reviews and ratings",
            "Inventory tracking"
        ],
        "docs": "/docs",
        "redoc": "/redoc"
    }