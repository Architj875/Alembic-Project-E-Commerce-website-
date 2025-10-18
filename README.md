# FastAPI with PostgreSQL, SQLAlchemy, and Alembic

This project demonstrates a comprehensive Python web backend using FastAPI, PostgreSQL database, SQLAlchemy ORM, and Alembic for schema migrations.

## 🎯 Features

- **User Management**: Basic CRUD operations for users
- **Customer Authentication**: Complete signup/login system with JWT tokens and session tracking
- **Product Management**: Full CRUD operations for products with SKU, pricing, and inventory
- **Product Categories**: Organize products into categories with active/inactive status
- **Shopping Cart**: Add, update, remove items with automatic cart management
- **Order Management**: Create orders from carts with status tracking and inventory updates
- **Address Management**: Manage customer addresses with default address support
- **Product Reviews**: Customer reviews with ratings (1-5 stars) and comments
- **Inventory Tracking**: Track stock levels, reorder levels, and restocking history
- **Payment Processing**: Payment management with transaction tracking and status updates
- **Order Tracking**: Real-time order tracking with location and status history
- **Database Migrations**: Alembic for version-controlled schema changes
- **API Documentation**: Auto-generated interactive docs with Swagger UI and ReDoc

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
    - Make sure you have installed PostgreSQL and pgAdmin.
    - Create a database named `mydatabase` and a user `myuser` with the password `mypassword`.
    - Ensure your local PostgreSQL server is running.

3.  **Configure the Database:**
    - Update the database URL in `app/database.py` and `alembic.ini` if needed
    - Default: `postgresql://postgres:password@localhost:5432/mydatabase`

### 3. Apply Database Migrations

Alembic is used to manage the database schema. To apply all migrations and bring the database to the latest version, run:
```bash
alembic upgrade head
```

This will create the following tables:
- `users` - User management
- `customers` - Customer accounts with authentication
- `customer_sessions` - Login/logout session tracking
- `products` - Product inventory management
- `product_categories` - Product categorization
- `shopping_carts` - Customer shopping carts
- `shopping_cart_items` - Items in shopping carts
- `orders` - Customer orders
- `addresses` - Customer addresses
- `reviews` - Product reviews and ratings
- `inventory` - Product inventory tracking
- `payments` - Order payments and transactions
- `order_tracking` - Order tracking history

### 4. Run the Application

Start the FastAPI development server:
```bash
uvicorn app.main:app --reload
```

The API will be available at: **http://localhost:8000**

### 5. Access API Documentation

FastAPI automatically generates interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📚 API Endpoints

### User Management
- `POST /users/` - Create a new user
- `GET /users/` - Get all users (with filtering)
- `GET /users/{user_id}` - Get user by ID
- `PUT /users/{user_id}` - Update user
- `DELETE /users/{user_id}` - Delete user

### Customer Authentication
- `POST /auth/signup` - Register new customer
- `POST /auth/login` - Authenticate customer
- `POST /auth/logout` - End session
- `GET /auth/sessions/{customer_id}` - View session history

### Product Management
- `POST /products/` - Create new product
- `GET /products/` - Get all products (with filtering)
- `GET /products/{product_id}` - Get product by ID
- `GET /products/sku/{sku}` - Get product by SKU
- `PUT /products/{product_id}` - Update product
- `DELETE /products/{product_id}` - Delete product

### Product Categories
- `POST /categories/` - Create new category
- `GET /categories/` - Get all categories (with filtering)
- `GET /categories/{category_id}` - Get category by ID
- `PUT /categories/{category_id}` - Update category
- `DELETE /categories/{category_id}` - Delete category

### Shopping Cart
- `GET /cart/{customer_id}` - Get customer's cart
- `POST /cart/{customer_id}/items` - Add item to cart
- `PUT /cart/items/{item_id}` - Update cart item
- `DELETE /cart/items/{item_id}` - Remove item from cart
- `DELETE /cart/{customer_id}/clear` - Clear cart

### Orders
- `POST /orders/?customer_id={id}` - Create order from cart
- `GET /orders/` - Get all orders (with filtering)
- `GET /orders/{order_id}` - Get order by ID
- `PUT /orders/{order_id}` - Update order status/address
- `DELETE /orders/{order_id}` - Delete order

### Addresses
- `POST /addresses/?customer_id={id}` - Create new address
- `GET /addresses/` - Get all addresses (with filtering)
- `GET /addresses/{address_id}` - Get address by ID
- `PUT /addresses/{address_id}` - Update address
- `DELETE /addresses/{address_id}` - Delete address

### Reviews
- `POST /reviews/?user_id={id}` - Create product review
- `GET /reviews/` - Get all reviews (with filtering)
- `GET /reviews/{review_id}` - Get review by ID
- `GET /reviews/products/{product_id}/average-rating` - Get average rating
- `PUT /reviews/{review_id}` - Update review
- `DELETE /reviews/{review_id}` - Delete review

### Inventory
- `POST /inventory/` - Create inventory record
- `GET /inventory/` - Get all inventory (with low stock filter)
- `GET /inventory/{inventory_id}` - Get inventory by ID
- `GET /inventory/products/{product_id}` - Get inventory by product
- `PUT /inventory/{inventory_id}` - Update inventory
- `POST /inventory/{inventory_id}/restock` - Restock inventory
- `DELETE /inventory/{inventory_id}` - Delete inventory

### Payments
- `POST /payments/` - Create payment
- `GET /payments/` - Get all payments (with filtering)
- `GET /payments/{payment_id}` - Get payment by ID
- `GET /payments/transaction/{transaction_id}` - Get payment by transaction ID
- `PUT /payments/{payment_id}` - Update payment
- `DELETE /payments/{payment_id}` - Delete payment

### Order Tracking 
- `POST /order-tracking/` - Create tracking entry
- `GET /order-tracking/` - Get all tracking entries
- `GET /order-tracking/{tracking_id}` - Get tracking entry by ID
- `GET /order-tracking/orders/{order_id}` - Get tracking history for order
- `GET /order-tracking/orders/{order_id}/latest` - Get latest tracking status
- `PUT /order-tracking/{tracking_id}` - Update tracking entry
- `DELETE /order-tracking/{tracking_id}` - Delete tracking entry

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

1. **users**
   - Basic user information (name, email, phone, address)

2. **customers**
   - Customer accounts with authentication
   - Fields: username, password_hash, email, full_name, is_active

3. **customer_sessions**
   - Login/logout session tracking
   - Fields: session_id, ip_address, login_time, logout_time, is_active

4. **products**
   - Product inventory management
   - Fields: sku, name, description, price, quantity

5. **product_categories**
   - Product categorization
   - Fields: product_id, category_id, category_name, description, is_active

6. **shopping_carts**
   - Customer shopping carts
   - Fields: customer_id, last_modified

7. **shopping_cart_items**
   - Items in shopping carts
   - Fields: cart_id, product_id, quantity

8. **orders**
   - Customer orders
   - Fields: customer_id, cart_id, address, order_status, total_amount, order_date

9. **addresses**
   - Customer addresses
   - Fields: customer_id, address, city, state, country, postal_code, is_default

10. **reviews**
    - Product reviews and ratings
    - Fields: user_id, product_id, rating, comment

11. **inventory**
    - Product inventory tracking
    - Fields: product_id, quantity_in_stock, reorder_level, last_restocked_at

12. **payments**
    - Order payments and transactions
    - Fields: order_id, transaction_id, payment_status, amount_paid, payment_date

13. **order_tracking**
    - Order tracking history
    - Fields: order_id, status, location, notes, timestamp

## 🔒 Security Features

- **Password Hashing**: Bcrypt for secure password storage
- **JWT Tokens**: Token-based authentication with expiration
- **Session Tracking**: IP address and timestamp logging
- **Input Validation**: Pydantic schemas for data validation

## 🛠️ Technology Stack

- **FastAPI**: Modern, fast web framework
- **PostgreSQL**: Robust relational database
- **SQLAlchemy**: Python SQL toolkit and ORM
- **Alembic**: Database migration tool
- **Pydantic**: Data validation using Python type hints
- **Passlib**: Password hashing library
- **Python-JOSE**: JWT token handling

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

## 📝 License

This project is open source and available under the MIT License.
Contributions, issues, and feature requests are welcome!

## 📧 Contact

For questions or support, please open an issue in the repository
