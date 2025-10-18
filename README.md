# FastAPI E-Commerce Platform with RBAC

A comprehensive e-commerce backend built with FastAPI, PostgreSQL, SQLAlchemy ORM, and Alembic migrations. Features role-based access control (RBAC), JWT authentication, and complete shopping functionality.

## 🎯 Features

### 🔐 Authentication & Authorization
- **JWT Token Authentication**: Secure token-based authentication for all endpoints
- **Role-Based Access Control (RBAC)**: Three user roles (CUSTOMER, ADMIN, SUPERADMIN)
- **Session Management**: Track user sessions with IP address and timestamps
- **Password Security**: Bcrypt password hashing with secure verification

### 👥 User Management
- **Unified User System**: Merged users and customers into single table
- **User Roles**: CUSTOMER (default), ADMIN, SUPERADMIN
- **Superadmin Endpoints**: Manage users, products, and moderate reviews
- **Account Management**: Signup, login, logout with session tracking

### 🛍️ E-Commerce Features
- **Product Management**: Full CRUD with SKU, pricing, quantity, and descriptions
- **Product Categories**: Organize products with active/inactive status
- **Shopping Cart**: Authenticated cart management with automatic user association
- **Order Management**: Create orders from carts with status tracking
- **Address Management**: Multiple addresses per user with default address support
- **Product Reviews**: User reviews with ratings (1-5 stars) and moderation
- **Inventory Tracking**: Stock levels, reorder points, and restocking history
- **Payment Processing**: Payment tracking with transaction IDs and status
- **Order Tracking**: Real-time order tracking with location and status history

### 🛠️ Technical Features
- **Database Migrations**: Alembic for version-controlled schema changes
- **API Documentation**: Auto-generated Swagger UI and ReDoc
- **Input Validation**: Pydantic schemas with comprehensive validation
- **Resource Ownership**: Users can only access/modify their own resources
- **PEP-8 Compliant**: All code follows Python style guidelines

## 🚀 How to Run the Project

### 1. Prerequisites

- Python 3.8+
- PostgreSQL installed and running locally.
- An active virtual environment is recommended.

### 2. Setup

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd fastapi_alembic_project
    ```

2.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure the Database:**
    - Make sure PostgreSQL is installed and running
    - Create a database named `fastapi_db`
    - Update the database URL in `app/database.py` and `alembic.ini` if needed
    - Default: `postgresql://postgres:password@localhost:5432/fastapi_db`

### 3. Apply Database Migrations

Alembic is used to manage the database schema. To apply all migrations and bring the database to the latest version, run:
```bash
alembic upgrade head
```

This will create the following tables:
- `users` - Unified user management with roles (CUSTOMER, ADMIN, SUPERADMIN)
- `user_sessions` - Login/logout session tracking with IP addresses
- `products` - Product inventory management
- `product_categories` - Product categorization
- `shopping_carts` - User shopping carts
- `shopping_cart_items` - Items in shopping carts
- `orders` - User orders with status tracking
- `addresses` - User addresses with default address support
- `reviews` - Product reviews with ratings and moderation
- `inventory` - Product inventory tracking
- `payments` - Order payments and transactions
- `order_tracking` - Order tracking history

### 4. Create Superadmin Account

Create your first superadmin account to access admin features:

```bash
python -c "from app.database import SessionLocal; from app import models; from app.auth import get_password_hash; db = SessionLocal(); admin = models.User(username='superadmin', password_hash=get_password_hash('admin123'), email='admin@example.com', full_name='Super Admin', is_active=True, role=models.UserRole.SUPERADMIN, is_superadmin=True); db.add(admin); db.commit(); print('✅ Superadmin created! Username: superadmin, Password: admin123'); db.close()"
```

**Default credentials:**
- Username: `superadmin`
- Password: `admin123`

⚠️ **Change the password immediately after first login!**

### 5. Run the Application

Start the FastAPI development server:
```bash
uvicorn app.main:app --reload
```

The API will be available at: **http://127.0.0.1:8000**

### 6. Access API Documentation

FastAPI automatically generates interactive API documentation:
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

### 7. Test the API

1. Go to http://127.0.0.1:8000/docs
2. Login with superadmin credentials
3. Click "Authorize" and paste your access token
4. Try the various endpoints!

## 📚 API Endpoints

### 🔐 Authentication (Public)
- `POST /auth/signup` - Register new user account
- `POST /auth/login` - Login and get JWT access token
- `POST /auth/logout` - Logout and end session
- `GET /auth/sessions/{user_id}` - View session history (authenticated)

### 👑 Superadmin Endpoints (Superadmin Only)
- `GET /superadmin/users` - List all users
- `PATCH /superadmin/users/{user_id}/role` - Change user role
- `POST /superadmin/products` - Create product
- `PUT /superadmin/products/{product_id}` - Update product
- `DELETE /superadmin/products/{product_id}` - Delete product
- `GET /superadmin/reviews` - List all reviews (including hidden)
- `PATCH /superadmin/reviews/{review_id}/visibility` - Moderate review visibility

### 📦 Products (Public Read, Superadmin Write)
- `GET /products/` - Get all products (public)
- `GET /products/{product_id}` - Get product by ID (public)
- `GET /products/sku/{sku}` - Get product by SKU (public)

### 📂 Categories (Public Read, Superadmin Write)
- `GET /categories/` - Get all categories (public)
- `GET /categories/{category_id}` - Get category by ID (public)

### 🛒 Shopping Cart (Authenticated)
- `GET /cart` - Get current user's cart
- `POST /cart/items` - Add item to cart
- `PUT /cart/items/{item_id}` - Update cart item quantity
- `DELETE /cart/items/{item_id}` - Remove item from cart
- `DELETE /cart/clear` - Clear entire cart

### 📦 Orders (Authenticated)
- `POST /orders/` - Create order from cart
- `GET /orders/` - Get current user's orders
- `GET /orders/{order_id}` - Get specific order (ownership verified)
- `PUT /orders/{order_id}` - Update order (ownership verified)
- `DELETE /orders/{order_id}` - Cancel order (ownership verified)

### 📍 Addresses (Authenticated)
- `POST /addresses/` - Create new address
- `GET /addresses/` - Get current user's addresses
- `GET /addresses/{address_id}` - Get specific address (ownership verified)
- `PUT /addresses/{address_id}` - Update address (ownership verified)
- `DELETE /addresses/{address_id}` - Delete address (ownership verified)

### ⭐ Reviews (Public Read, Authenticated Write)
- `POST /reviews/` - Create product review (authenticated)
- `GET /reviews/` - Get all visible reviews (public)
- `GET /reviews/{review_id}` - Get review by ID (public)
- `GET /reviews/products/{product_id}/average-rating` - Get average rating (public)
- `PUT /reviews/{review_id}` - Update review (ownership verified)
- `DELETE /reviews/{review_id}` - Delete review (ownership verified)

### 📊 Inventory (Public Read, Superadmin Write)
- `GET /inventory/` - Get all inventory (public)
- `GET /inventory/{inventory_id}` - Get inventory by ID (public)
- `GET /inventory/products/{product_id}` - Get inventory by product (public)

### 💳 Payments (Authenticated)
- `POST /payments/` - Create payment (authenticated)
- `GET /payments/` - Get current user's payments
- `GET /payments/{payment_id}` - Get payment by ID (ownership verified)
- `GET /payments/transaction/{transaction_id}` - Get payment by transaction ID
- `PUT /payments/{payment_id}` - Update payment (ownership verified)
- `DELETE /payments/{payment_id}` - Delete payment (ownership verified)

### 📍 Order Tracking (Public Read)
- `GET /order-tracking/` - Get all tracking entries
- `GET /order-tracking/{tracking_id}` - Get tracking entry by ID
- `GET /order-tracking/orders/{order_id}` - Get tracking history for order
- `GET /order-tracking/orders/{order_id}/latest` - Get latest tracking status

## 🧪 Testing

### Test Authentication API
```bash
python test_auth_api.py
```

### Test Products API
```bash
python test_products_api.py
```

### Test Shopping APIs (Cart, Categories, Orders)
```bash
python test_shopping_apis.py
```

### Test New APIs (Addresses, Reviews, Inventory)
```bash
python test_new_apis.py
```

### Test Payments & Tracking APIs
```bash
python test_payments_tracking.py
```

## 📖 Documentation

- **Quick Start Guide**: `QUICK_START.md`
- **Authentication API**: `AUTHENTICATION_API.md`
- **Products API**: `PRODUCTS_API.md`
- **Shopping APIs**: `SHOPPING_APIS_DOCUMENTATION.md` (Cart, Categories, Orders)
- **New APIs**: `NEW_APIS_DOCUMENTATION.md` (Addresses, Reviews, Inventory)
- **Payments & Tracking**: `PAYMENTS_TRACKING_DOCUMENTATION.md` (Payments, Order Tracking)
- **Implementation Details**:
  - `IMPLEMENTATION_SUMMARY.md` (Authentication)
  - `PRODUCTS_IMPLEMENTATION_SUMMARY.md` (Products)
  - `SHOPPING_IMPLEMENTATION_SUMMARY.md` (Shopping)

## 🗄️ Database Schema

### Tables

1. **users** (Unified user management)
   - `id` - Primary key
   - `username` - Unique username
   - `password_hash` - Bcrypt hashed password
   - `email` - User email
   - `full_name` - Full name
   - `role` - User role (CUSTOMER, ADMIN, SUPERADMIN)
   - `is_superadmin` - Boolean flag for superadmin access
   - `is_active` - Account active status
   - `created_at`, `updated_at` - Timestamps

2. **user_sessions**
   - Login/logout session tracking
   - Fields: user_id, session_id, ip_address, login_time, logout_time, is_active

3. **products**
   - Product inventory management
   - Fields: sku (unique), name, description, price, quantity

4. **product_categories**
   - Product categorization
   - Fields: product_id, category_id, category_name, description, is_active

5. **shopping_carts**
   - User shopping carts
   - Fields: user_id, last_modified

6. **shopping_cart_items**
   - Items in shopping carts
   - Fields: cart_id, product_id, quantity

7. **orders**
   - User orders
   - Fields: user_id, cart_id, address, order_status, total_amount, order_date

8. **addresses**
   - User addresses
   - Fields: user_id, address, city, state, country, postal_code, is_default

9. **reviews**
   - Product reviews and ratings
   - Fields: user_id, product_id, rating, comment, is_visible (for moderation)

10. **inventory**
    - Product inventory tracking
    - Fields: product_id, quantity_in_stock, reorder_level, last_restocked_at

11. **payments**
    - Order payments and transactions
    - Fields: order_id, transaction_id, payment_status, amount_paid, payment_date

12. **order_tracking**
    - Order tracking history
    - Fields: order_id, status, location, notes, timestamp

## 🔒 Security Features

- **Password Hashing**: Bcrypt for secure password storage (72-byte limit)
- **JWT Tokens**: Token-based authentication with 30-minute expiration
- **Role-Based Access Control**: Three-tier permission system
- **Resource Ownership**: Users can only access their own data
- **Session Tracking**: IP address and timestamp logging
- **Input Validation**: Pydantic schemas for comprehensive data validation
- **SQL Injection Protection**: SQLAlchemy ORM prevents SQL injection
- **CORS Configuration**: Configurable cross-origin resource sharing

## 🛠️ Technology Stack

- **FastAPI**: Modern, fast web framework with automatic API documentation
- **PostgreSQL**: Robust relational database with ACID compliance
- **SQLAlchemy**: Python SQL toolkit and ORM with relationship management
- **Alembic**: Database migration tool for version control
- **Pydantic**: Data validation using Python type hints
- **Bcrypt**: Secure password hashing algorithm
- **Python-JOSE**: JWT token creation and verification
- **Uvicorn**: Lightning-fast ASGI server

## 📁 Project Structure

```
fastapi_alembic_project/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── auth.py              # Authentication utilities
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── crud.py              # Database operations
│   ├── database.py          # Database connection
│   └── routers/
│       ├── __init__.py
│       ├── auth.py          # Authentication endpoints
│       └── products.py      # Product endpoints
├── alembic/
│   ├── versions/            # Migration files
│   └── env.py               # Alembic configuration
├── tests/
│   ├── test_auth_api.py     # Auth API tests
│   └── test_products_api.py # Products API tests
├── requirements.txt         # Python dependencies
├── alembic.ini             # Alembic configuration
└── README.md               # This file
```

## 🚀 Quick Examples

### Create a Customer and Login
```python
import requests

# Signup
response = requests.post("http://localhost:8000/auth/signup", json={
    "username": "john_doe",
    "password": "SecurePass123!",
    "email": "john@example.com"
})
token = response.json()["access_token"]

# Login
response = requests.post("http://localhost:8000/auth/login", json={
    "username": "john_doe",
    "password": "SecurePass123!"
})
```

### Create and Manage Products
```python
# Create product
response = requests.post("http://localhost:8000/products/", json={
    "sku": "LAPTOP-001",
    "name": "Dell XPS 15",
    "price": 1299.99,
    "quantity": 25
})
product = response.json()

# Get all products
products = requests.get("http://localhost:8000/products/").json()

# Update product
requests.put(f"http://localhost:8000/products/{product['id']}", json={
    "price": 1199.99,
    "quantity": 30
})
```

### Complete Shopping Workflow
```python
# 1. Customer signup
signup = requests.post("http://localhost:8000/auth/signup", json={
    "username": "customer1",
    "password": "SecurePass123!",
    "email": "customer1@example.com"
})
customer_id = signup.json()["customer"]["id"]

# 2. Add product to cart
requests.post(f"http://localhost:8000/cart/{customer_id}/items", json={
    "product_id": 1,
    "quantity": 2
})

# 3. Get cart
cart = requests.get(f"http://localhost:8000/cart/{customer_id}").json()

# 4. Create order
order = requests.post(
    f"http://localhost:8000/orders/?customer_id={customer_id}",
    json={
        "cart_id": cart["id"],
        "address": "123 Main St, City, State 12345"
    }
).json()

# 5. Update order status
requests.put(f"http://localhost:8000/orders/{order['id']}", json={
    "order_status": "confirmed"
})
```

## 🔧 Configuration

### Database Connection
Update the database URL in:
- `app/database.py`
- `alembic.ini`

### JWT Secret Key
⚠️ **Important**: Change the `SECRET_KEY` in `app/auth.py` before production!

```python
# In app/auth.py
SECRET_KEY = "your-secure-random-secret-key-here"
```

Generate a secure key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## 📤 Pushing to GitHub

### Initial Setup

1. **Initialize Git repository** (if not already done):
   ```bash
   git init
   ```

2. **Add all files to staging**:
   ```bash
   git add .
   ```

3. **Create initial commit**:
   ```bash
   git commit -m "Initial commit: FastAPI e-commerce platform with RBAC"
   ```

4. **Add your GitHub repository as remote**:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   ```

5. **Push to GitHub**:
   ```bash
   git branch -M main
   git push -u origin main
   ```

### Important Files to Exclude

The `.gitignore` file already excludes:
- `venv/` - Virtual environment (never commit this!)
- `__pycache__/` - Python cache files
- `.env` - Environment variables with secrets
- `*.log` - Log files
- `.vscode/`, `.idea/` - IDE settings

### What Gets Committed

✅ **Include:**
- All Python source code (`app/`, `alembic/`)
- Configuration files (`alembic.ini`, `requirements.txt`)
- Documentation (`*.md` files)
- `.gitignore` file

❌ **Exclude:**
- Virtual environment (`venv/`)
- Database files
- Environment variables (`.env`)
- IDE settings
- Python cache files

### Updating Your Repository

After making changes:

```bash
# Check what changed
git status

# Add specific files
git add app/models.py app/schemas.py

# Or add all changes
git add .

# Commit with descriptive message
git commit -m "Add user authentication feature"

# Push to GitHub
git push
```

### Best Practices

1. **Commit Often**: Make small, focused commits
2. **Write Clear Messages**: Describe what and why, not how
3. **Never Commit Secrets**: Keep passwords, API keys in `.env` (excluded by `.gitignore`)
4. **Review Before Pushing**: Use `git status` and `git diff`
5. **Use Branches**: Create feature branches for new work

### Example Workflow

```bash
# Create a new feature branch
git checkout -b feature/add-wishlist

# Make your changes
# ... edit files ...

# Stage and commit
git add .
git commit -m "Add wishlist functionality"

# Push branch to GitHub
git push -u origin feature/add-wishlist

# Create pull request on GitHub
# After review and merge, switch back to main
git checkout main
git pull
```

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📧 Contact

For questions or support, please open an issue in the repository.

## 🙏 Acknowledgments

- FastAPI documentation and community
- SQLAlchemy and Alembic teams
- PostgreSQL community

---

**Made with ❤️ using FastAPI**