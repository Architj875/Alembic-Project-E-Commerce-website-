# Project Structure

## 📁 Clean Directory Layout

```
fastapi_alembic_project/
├── app/                          # Main application package
│   ├── __init__.py              # Package initializer
│   ├── main.py                  # FastAPI application entry point
│   ├── auth.py                  # Authentication utilities (bcrypt, JWT)
│   ├── database.py              # Database connection and session
│   ├── models.py                # SQLAlchemy ORM models
│   ├── schemas.py               # Pydantic schemas for validation
│   ├── crud.py                  # Database CRUD operations
│   └── routers/                 # API route handlers
│       ├── __init__.py
│       ├── auth.py              # Authentication endpoints
│       ├── products.py          # Product management
│       ├── cart.py              # Shopping cart
│       ├── categories.py        # Product categories
│       ├── orders.py            # Order management
│       ├── addresses.py         # Customer addresses
│       ├── reviews.py           # Product reviews
│       ├── inventory.py         # Inventory tracking
│       ├── payments.py          # Payment processing
│       └── order_tracking.py    # Order tracking
│
├── alembic/                     # Database migrations
│   ├── versions/                # Migration version files
│   ├── env.py                   # Alembic environment config
│   └── script.py.mako           # Migration template
│
├── venv/                        # Virtual environment (not in git)
│
├── .gitignore                   # Git ignore rules
├── alembic.ini                  # Alembic configuration
├── requirements.txt             # Python dependencies
├── README.md                    # Main project documentation
├── COMPLETE_PROJECT_SUMMARY.md  # Detailed implementation summary
└── PROJECT_STRUCTURE.md         # This file
```

## 🗂️ File Purposes

### Core Application Files

- **`app/main.py`** - FastAPI app initialization, router registration, CORS setup
- **`app/auth.py`** - Password hashing (bcrypt), JWT token management, session ID generation
- **`app/database.py`** - PostgreSQL connection, SQLAlchemy engine, session management
- **`app/models.py`** - Database table definitions (13 tables)
- **`app/schemas.py`** - Request/response validation schemas (36+ schemas)
- **`app/crud.py`** - Database operations for all models (70+ functions)

### API Routers (10 modules)

Each router handles specific business logic:

1. **auth.py** - Customer signup, login, logout, session management
2. **products.py** - Product CRUD, SKU management
3. **cart.py** - Shopping cart operations, item management
4. **categories.py** - Product categorization
5. **orders.py** - Order creation, status updates, inventory sync
6. **addresses.py** - Customer address management, default address
7. **reviews.py** - Product reviews, ratings, average calculation
8. **inventory.py** - Stock tracking, reorder levels, restocking
9. **payments.py** - Payment processing, transaction tracking
10. **order_tracking.py** - Order status history, location tracking

### Database Migrations

- **`alembic/versions/`** - Contains all migration files (7 migrations)
- **`alembic.ini`** - Alembic configuration (database URL, etc.)
- **`alembic/env.py`** - Migration environment setup

### Configuration Files

- **`.gitignore`** - Excludes venv, __pycache__, .env, etc.
- **`requirements.txt`** - Python package dependencies
- **`README.md`** - Setup instructions, API documentation
- **`COMPLETE_PROJECT_SUMMARY.md`** - Full feature list and statistics

## 📊 Database Schema (13 Tables)

1. **users** - Basic user information
2. **customers** - Customer accounts with authentication
3. **customer_sessions** - Login sessions with IP tracking
4. **products** - Product catalog
5. **product_categories** - Product categorization
6. **shopping_carts** - Customer shopping carts
7. **shopping_cart_items** - Items in carts
8. **orders** - Customer orders
9. **addresses** - Customer addresses
10. **reviews** - Product reviews and ratings
11. **inventory** - Stock levels and reorder tracking
12. **payments** - Payment transactions
13. **order_tracking** - Order status history

## 🚀 Quick Commands

### Start Development Server
```bash
uvicorn app.main:app --reload
```

### Run Database Migration
```bash
alembic upgrade head
```

### Create New Migration
```bash
alembic revision --autogenerate -m "description"
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

## 📝 Notes

- All Python cache files (`__pycache__`) are excluded from git
- Virtual environment (`venv/`) is excluded from git
- Database credentials should be in `.env` file (not committed)
- All code follows PEP-8 standards
- API documentation available at `/docs` when server is running

