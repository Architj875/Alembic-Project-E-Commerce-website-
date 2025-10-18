# API Authentication Quick Reference Guide

## 🚀 Quick Start

### 1. Sign Up
```bash
POST /auth/signup
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password",
  "email": "your@email.com",
  "full_name": "Your Name"
}
```

### 2. Login
```bash
POST /auth/login
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}

Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": 1,
  "username": "your_username"
}
```

### 3. Use the Token
```bash
GET /cart
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 📚 Endpoint Reference

### Public Endpoints (No Authentication)

#### Authentication
- `POST /auth/signup` - Create new account
- `POST /auth/login` - Get access token

#### Products
- `GET /products` - List all products
- `GET /products/{product_id}` - Get product details
- `GET /products/sku/{sku}` - Get product by SKU

#### Categories
- `GET /categories` - List all categories
- `GET /categories/{category_id}` - Get category details

#### Reviews (Read Only)
- `GET /reviews` - List all reviews
- `GET /reviews/{review_id}` - Get review details
- `GET /reviews/products/{product_id}/average-rating` - Get product rating

---

### Protected Endpoints (Require Authentication)

#### Shopping Cart
```bash
# Get your cart
GET /cart
Authorization: Bearer <token>

# Add item to cart
POST /cart/items
Authorization: Bearer <token>
Content-Type: application/json
{
  "product_id": 1,
  "quantity": 2
}

# Update cart item quantity
PUT /cart/items/{item_id}
Authorization: Bearer <token>
Content-Type: application/json
{
  "quantity": 5
}

# Remove item from cart
DELETE /cart/items/{item_id}
Authorization: Bearer <token>

# Clear entire cart
DELETE /cart/clear
Authorization: Bearer <token>
```

#### Orders
```bash
# Create order from cart
POST /orders
Authorization: Bearer <token>
Content-Type: application/json
{
  "cart_id": 1,
  "address": "123 Main St, City, State, ZIP"
}

# Get your orders
GET /orders
Authorization: Bearer <token>

# Get your orders with filters
GET /orders?order_status=pending&skip=0&limit=10
Authorization: Bearer <token>

# Get specific order
GET /orders/{order_id}
Authorization: Bearer <token>

# Update order
PUT /orders/{order_id}
Authorization: Bearer <token>
Content-Type: application/json
{
  "address": "New address",
  "order_status": "confirmed"
}

# Delete order
DELETE /orders/{order_id}
Authorization: Bearer <token>
```

#### Addresses
```bash
# Create address
POST /addresses
Authorization: Bearer <token>
Content-Type: application/json
{
  "address": "123 Main St",
  "city": "New York",
  "state": "NY",
  "country": "USA"
}

# Get your addresses
GET /addresses
Authorization: Bearer <token>

# Get specific address
GET /addresses/{address_id}
Authorization: Bearer <token>

# Update address
PUT /addresses/{address_id}
Authorization: Bearer <token>
Content-Type: application/json
{
  "address": "456 Oak Ave",
  "city": "Los Angeles"
}

# Delete address
DELETE /addresses/{address_id}
Authorization: Bearer <token>
```

#### Reviews
```bash
# Create review
POST /reviews
Authorization: Bearer <token>
Content-Type: application/json
{
  "product_id": 1,
  "rating": 5,
  "comment": "Great product!"
}

# Update your review
PUT /reviews/{review_id}
Authorization: Bearer <token>
Content-Type: application/json
{
  "rating": 4,
  "comment": "Updated review"
}

# Delete your review
DELETE /reviews/{review_id}
Authorization: Bearer <token>
```

#### Payments
```bash
# Create payment
POST /payments
Authorization: Bearer <token>
Content-Type: application/json
{
  "order_id": 1,
  "transaction_id": "TXN123456",
  "amount_paid": 99.99,
  "payment_status": "completed"
}

# Get your payments
GET /payments
Authorization: Bearer <token>

# Get payments for specific order
GET /payments?order_id=1
Authorization: Bearer <token>

# Get specific payment
GET /payments/{payment_id}
Authorization: Bearer <token>

# Get payment by transaction ID
GET /payments/transaction/{transaction_id}
Authorization: Bearer <token>

# Update payment
PUT /payments/{payment_id}
Authorization: Bearer <token>
Content-Type: application/json
{
  "payment_status": "refunded"
}

# Delete payment
DELETE /payments/{payment_id}
Authorization: Bearer <token>
```

---

### Superadmin Endpoints (Require Superadmin Role)

#### Product Management
```bash
# Create product
POST /superadmin/products
Authorization: Bearer <superadmin_token>
Content-Type: application/json
{
  "name": "New Product",
  "sku": "PROD-001",
  "price": 29.99,
  "quantity": 100,
  "description": "Product description"
}

# Update product
PUT /superadmin/products/{product_id}
Authorization: Bearer <superadmin_token>
Content-Type: application/json
{
  "name": "Updated Product",
  "price": 39.99
}

# Update product price
PATCH /superadmin/products/{product_id}/price
Authorization: Bearer <superadmin_token>
Content-Type: application/json
{
  "price": 49.99
}

# Delete product
DELETE /superadmin/products/{product_id}
Authorization: Bearer <superadmin_token>
```

#### User Management
```bash
# List all users
GET /superadmin/users
Authorization: Bearer <superadmin_token>

# List users with filters
GET /superadmin/users?role=customer&is_active=true
Authorization: Bearer <superadmin_token>

# Update user role
PATCH /superadmin/users/{user_id}/role
Authorization: Bearer <superadmin_token>
Content-Type: application/json
{
  "role": "admin",
  "is_superadmin": false
}

# Delete user
DELETE /superadmin/users/{user_id}
Authorization: Bearer <superadmin_token>
```

#### Review Moderation
```bash
# Hide/show review
PATCH /superadmin/reviews/{review_id}/visibility
Authorization: Bearer <superadmin_token>
Content-Type: application/json
{
  "is_visible": false
}
```

---

## 🔑 Authentication Headers

### Standard Format
```
Authorization: Bearer <your_access_token>
```

### Example
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huX2RvZSIsInVzZXJfaWQiOjEsImV4cCI6MTY0MDk5NTIwMH0.abc123...
```

---

## ⚠️ Common Errors

### 401 Unauthorized
**Cause:** Missing, invalid, or expired token  
**Solution:** Login again to get a new token

```json
{
  "detail": "Could not validate credentials"
}
```

### 403 Forbidden
**Cause:** Trying to access resource you don't own  
**Solution:** Only access your own resources

```json
{
  "detail": "You can only view your own orders"
}
```

**Cause:** Account is inactive  
**Solution:** Contact administrator

```json
{
  "detail": "User account is inactive"
}
```

**Cause:** Insufficient permissions (not superadmin)  
**Solution:** Request superadmin access

```json
{
  "detail": "Superadmin access required"
}
```

### 404 Not Found
**Cause:** Resource doesn't exist  
**Solution:** Check the ID and try again

```json
{
  "detail": "Order with ID 123 not found"
}
```

---

## 💡 Best Practices

### 1. Token Storage
- **Frontend:** Store in memory or httpOnly cookie
- **Mobile:** Use secure storage (Keychain/Keystore)
- **Never:** Store in localStorage (XSS vulnerable)

### 2. Token Refresh
- Check token expiration before requests
- Implement automatic re-login when token expires
- Handle 401 errors gracefully

### 3. Error Handling
```javascript
// Example: JavaScript/TypeScript
async function makeAuthenticatedRequest(url, options = {}) {
  const token = getStoredToken();
  
  const response = await fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
  
  if (response.status === 401) {
    // Token expired, redirect to login
    redirectToLogin();
  } else if (response.status === 403) {
    // Forbidden, show error message
    showError('You do not have permission to access this resource');
  }
  
  return response.json();
}
```

### 4. Security
- Always use HTTPS in production
- Never log or expose tokens
- Implement token expiration
- Use strong passwords (min 8 characters)

---

## 🧪 Testing with cURL

### Complete Workflow Example
```bash
# 1. Sign up
curl -X POST "http://127.0.0.1:8000/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123",
    "email": "test@example.com",
    "full_name": "Test User"
  }'

# 2. Login and save token
TOKEN=$(curl -X POST "http://127.0.0.1:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }' | jq -r '.access_token')

# 3. Get your cart
curl -X GET "http://127.0.0.1:8000/cart" \
  -H "Authorization: Bearer $TOKEN"

# 4. Add item to cart
curl -X POST "http://127.0.0.1:8000/cart/items" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 1,
    "quantity": 2
  }'

# 5. Create order
curl -X POST "http://127.0.0.1:8000/orders" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "cart_id": 1,
    "address": "123 Main St, City, State, ZIP"
  }'
```

---

## 📖 Additional Resources

- **API Documentation:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc
- **Implementation Details:** See `AUTHENTICATION_IMPLEMENTATION.md`
- **RBAC Guide:** See `RBAC_IMPLEMENTATION_SUMMARY.md`

---

**Last Updated:** 2025-10-16  
**API Version:** 2.1.0

