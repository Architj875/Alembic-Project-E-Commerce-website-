# Changelog

All notable changes to this project will be documented in this file.

## [2.1.0] - 2025-10-16

### 🔐 Added - JWT Authentication Across All Endpoints

#### Security Enhancements
- Implemented comprehensive JWT-based authentication for all user-specific endpoints
- Added automatic user identification from JWT access tokens
- Implemented ownership verification for all resource access
- Added protection against unauthorized access to other users' data

#### Shopping Cart (`/cart`)
- **Changed:** `GET /cart/{customer_id}` → `GET /cart` (user auto-identified from token)
- **Changed:** `POST /cart/{customer_id}/items` → `POST /cart/items` (user auto-identified from token)
- **Changed:** `DELETE /cart/{customer_id}/clear` → `DELETE /cart/clear` (user auto-identified from token)
- **Added:** Ownership verification for cart item updates and deletions
- **Added:** `current_user` dependency to all endpoints

#### Orders (`/orders`)
- **Changed:** `POST /orders` - Removed `customer_id` parameter (user auto-identified from token)
- **Changed:** `GET /orders` - Removed `customer_id` filter (automatically filtered to current user)
- **Added:** Ownership verification for all order operations (get, update, delete)
- **Added:** `current_user` dependency to all endpoints
- **Security:** Users can only access their own orders

#### Addresses (`/addresses`)
- **Changed:** `POST /addresses` - Removed `customer_id` parameter (user auto-identified from token)
- **Changed:** `GET /addresses` - Removed `customer_id` filter (automatically filtered to current user)
- **Added:** Ownership verification for all address operations (get, update, delete)
- **Added:** `current_user` dependency to all endpoints
- **Security:** Users can only access their own addresses

#### Reviews (`/reviews`)
- **Changed:** `POST /reviews` - Removed `user_id` parameter (user auto-identified from token)
- **Added:** Ownership verification for review updates and deletions
- **Added:** `current_user` dependency to create, update, and delete endpoints
- **Kept:** Public read access for GET endpoints (browsing reviews)
- **Security:** Users can only update/delete their own reviews

#### Payments (`/payments`)
- **Added:** Ownership verification for all payment operations
- **Changed:** `GET /payments` - Automatically filtered to current user's orders
- **Added:** Order ownership verification for payment creation
- **Added:** `current_user` dependency to all endpoints
- **Security:** Users can only access payments for their own orders

#### Dependencies
- **Added:** `get_current_active_user` dependency imported in all protected routers
- **Enhanced:** Consistent error handling with 401 Unauthorized and 403 Forbidden responses

### 📚 Documentation
- **Added:** `AUTHENTICATION_IMPLEMENTATION.md` - Comprehensive authentication implementation guide
- **Added:** `API_AUTHENTICATION_GUIDE.md` - Quick reference guide for API consumers
- **Updated:** API documentation with new authentication requirements

### 🔄 Breaking Changes

#### Removed Parameters
- `customer_id` from cart endpoints
- `customer_id` from order creation endpoint
- `customer_id` filter from orders list endpoint
- `customer_id` from address creation endpoint
- `customer_id` filter from addresses list endpoint
- `user_id` from review creation endpoint

#### Required Headers
All protected endpoints now require:
```
Authorization: Bearer <access_token>
```

#### Automatic Filtering
- Orders list automatically filtered to current user
- Addresses list automatically filtered to current user
- Payments list automatically filtered to current user's orders

### 🛡️ Security Improvements
- **Prevented:** Unauthorized access to other users' carts
- **Prevented:** Unauthorized access to other users' orders
- **Prevented:** Unauthorized access to other users' addresses
- **Prevented:** Unauthorized modification of other users' reviews
- **Prevented:** Unauthorized access to other users' payment information
- **Added:** Consistent 403 Forbidden responses for ownership violations
- **Added:** Active user verification (inactive accounts cannot access protected endpoints)

### 📊 Endpoint Summary

| Category | Public | Authenticated | Superadmin |
|----------|--------|---------------|------------|
| Auth | ✅ | - | - |
| Products (GET) | ✅ | - | - |
| Categories (GET) | ✅ | - | - |
| Reviews (GET) | ✅ | - | - |
| Shopping Cart | - | ✅ | - |
| Orders | - | ✅ | - |
| Addresses | - | ✅ | - |
| Reviews (POST/PUT/DELETE) | - | ✅ | - |
| Payments | - | ✅ | - |
| Product Management | - | - | ✅ |
| User Management | - | - | ✅ |
| Review Moderation | - | - | ✅ |

---

## [2.0.0] - 2025-10-16

### 🔐 Added - Role-Based Access Control (RBAC)

#### Database Schema Changes
- **Merged:** `users` and `customers` tables into single `users` table
- **Added:** `role` field (enum: CUSTOMER, ADMIN, SUPERADMIN)
- **Added:** `is_superadmin` boolean field
- **Added:** `is_visible` field to reviews table for moderation
- **Updated:** All foreign keys from `customer_id` to `user_id`
- **Migrated:** All existing customer data to users table

#### New Features
- **Added:** Superadmin product management endpoints
- **Added:** Superadmin user management endpoints
- **Added:** Superadmin review moderation endpoints
- **Added:** Authorization middleware (`app/dependencies.py`)
- **Added:** Role-based access control with three levels (Customer, Admin, Superadmin)

#### Superadmin Endpoints
- `POST /superadmin/products` - Create product
- `PUT /superadmin/products/{product_id}` - Update product
- `DELETE /superadmin/products/{product_id}` - Delete product
- `PATCH /superadmin/products/{product_id}/price` - Update product price
- `GET /superadmin/users` - List all users
- `DELETE /superadmin/users/{user_id}` - Delete user
- `PATCH /superadmin/users/{user_id}/role` - Update user role
- `PATCH /superadmin/reviews/{review_id}/visibility` - Moderate review visibility

#### Models & Schemas
- **Added:** `UserRole` enum in models
- **Added:** `UserRoleEnum` in schemas
- **Updated:** User model with role fields
- **Added:** Backward compatibility aliases

#### Documentation
- **Added:** `RBAC_IMPLEMENTATION_SUMMARY.md`
- **Added:** `CREATE_SUPERADMIN.md`
- **Added:** `PROJECT_STRUCTURE.md`

### 🔄 Backward Compatibility
- **Maintained:** All existing API endpoints
- **Maintained:** Authentication flow (JWT tokens)
- **Maintained:** Session management
- **Added:** Schema aliases for smooth transition

---

## [1.0.0] - Initial Release

### Features
- User authentication (signup, login, logout)
- Product management
- Shopping cart functionality
- Order management
- Address management
- Product reviews and ratings
- Payment processing
- Inventory tracking
- Order tracking
- Product categories

### Technologies
- FastAPI web framework
- PostgreSQL database
- SQLAlchemy ORM
- Alembic migrations
- JWT authentication
- Bcrypt password hashing
- Pydantic validation

---

## Migration Guide

### From 1.0.0 to 2.0.0 (RBAC)
1. Run database migration: `alembic upgrade head`
2. Create superadmin user (see `CREATE_SUPERADMIN.md`)
3. Update any direct database queries to use `users` table instead of `customers`

### From 2.0.0 to 2.1.0 (JWT Authentication)
1. **Update API Clients:**
   - Remove `customer_id` and `user_id` parameters from requests
   - Add `Authorization: Bearer <token>` header to all protected endpoints
   - Handle 401 and 403 error responses

2. **Update Frontend:**
   - Store JWT token after login
   - Include token in all authenticated requests
   - Implement token refresh logic
   - Handle authentication errors

3. **Testing:**
   - Test all endpoints with valid tokens
   - Test ownership verification (try accessing other users' resources)
   - Test with expired tokens
   - Test with inactive user accounts

---

## Upcoming Features

### Planned for 2.2.0
- [ ] Token refresh endpoint
- [ ] Password reset functionality
- [ ] Email verification
- [ ] Two-factor authentication (2FA)
- [ ] Rate limiting
- [ ] API key authentication for third-party integrations

### Planned for 2.3.0
- [ ] Wishlist functionality
- [ ] Product recommendations
- [ ] Order history export
- [ ] Advanced search and filtering
- [ ] Bulk operations for superadmins

### Planned for 3.0.0
- [ ] WebSocket support for real-time updates
- [ ] GraphQL API
- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] Automated testing suite

---

## Support

For questions or issues:
- Check the documentation in `/docs` directory
- Review API documentation at http://127.0.0.1:8000/docs
- See implementation guides in project root

---

**Current Version:** 2.1.0  
**Last Updated:** 2025-10-16  
**Status:** Production Ready

