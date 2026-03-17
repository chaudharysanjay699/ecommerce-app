# Ecom Grocery App — API Reference
> **For React Frontend Developers**
> Base URL: `http://localhost:8000/api/v1`
> Interactive Docs: http://localhost:8000/api/v1/docs

---

## Table of Contents
1. [Authentication & Headers](#1-authentication--headers)
2. [Common Data Types](#2-common-data-types)
3. [Error Responses](#3-error-responses)
4. [Auth Endpoints](#4-auth-endpoints)
5. [Categories](#5-categories)
6. [Products](#6-products)
7. [Cart](#7-cart)
8. [Orders](#8-orders)
9. [Order Tracking](#9-order-tracking)
10. [Admin Panel](#10-admin-panel)
11. [Business Rules](#11-business-rules)
12. [React Integration Tips](#12-react-integration-tips)

---

## 1. Authentication & Headers

### JWT Flow
The API uses two tokens:
- **Access token** — short-lived, sent on every authenticated request
- **Refresh token** — long-lived, used only to obtain a new access token

### Sending the Access Token
Include the token in the `Authorization` header on every protected request:

```http
Authorization: Bearer <access_token>
```

### Refreshing Tokens
When you receive a `401 Unauthorized`, call `POST /auth/refresh` with the refresh token to get a new pair.

---

## 2. Common Data Types

| Type | Format | Example |
|------|--------|---------|
| `id` | UUID string | `"3fa85f64-5717-4562-b3fc-2c963f66afa6"` |
| `created_at` | ISO 8601 UTC | `"2026-03-10T09:30:00.000Z"` |
| `updated_at` | ISO 8601 UTC | `"2026-03-10T09:30:00.000Z"` |
| `price` | float | `49.99` |
| `discount_percent` | float (0–100) | `15.5` |

### OrderStatus Values
```
placed → confirmed → packed → out_for_delivery → delivered
                                              ↘ cancelled
```

| Value | Meaning |
|-------|---------|
| `placed` | Order just placed by customer |
| `confirmed` | Admin confirmed the order |
| `packed` | Items packed and ready |
| `out_for_delivery` | Delivery partner picked up |
| `delivered` | Successfully delivered |
| `cancelled` | Cancelled (by admin or customer) |

### CategoryType Values
```
VEGETABLE | GROCERY | BASKET | COPY_PEN
```

---

## 3. Error Responses

All errors follow this shape:

```json
{
  "detail": "Human-readable error message"
}
```

| HTTP Status | Meaning |
|-------------|---------|
| `400` | Bad request / validation failure |
| `401` | Missing or invalid/expired token |
| `403` | Authenticated but not authorized (e.g., non-admin) |
| `404` | Resource not found |
| `409` | Conflict (e.g., phone already registered) |
| `422` | Pydantic validation error (check `detail` array) |
| `500` | Server error |

**Validation error shape (422):**
```json
{
  "detail": [
    {
      "loc": ["body", "phone"],
      "msg": "Value error, invalid phone format",
      "type": "value_error"
    }
  ]
}
```

---

## 4. Auth Endpoints

### Register
```
POST /auth/register
```
**Request body:**
```json
{
  "full_name": "John Doe",
  "phone": "+919876543210",
  "email": "john@example.com",
  "password": "SecurePass1!"
}
```
- `email` is optional
- `phone` pattern: `+` optional, 7–15 digits
- `password` minimum 8 characters

**Response `201`:**
```json
{
  "id": "uuid",
  "full_name": "John Doe",
  "phone": "+919876543210",
  "email": "john@example.com",
  "avatar_url": null,
  "is_active": true,
  "is_verified": false,
  "is_admin": false,
  "created_at": "2026-03-10T09:00:00Z",
  "updated_at": "2026-03-10T09:00:00Z"
}
```

---

### Login
```
POST /auth/login
```
**Request body:**
```json
{
  "phone": "+919876543210",
  "password": "SecurePass1!"
}
```

**Response `200`:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

### Refresh Token
```
POST /auth/refresh
```
**Request body:**
```json
{
  "refresh_token": "<your_refresh_token>"
}
```

**Response `200`:** Same as Login response (new token pair).

---

### Send OTP
```
POST /auth/otp/send
```
**Request body:**
```json
{
  "phone": "+919876543210"
}
```

**Response `200`:**
```json
{
  "message": "OTP sent",
  "debug_code": "123456"
}
```
> **Note:** `debug_code` is only present in development. Remove dependency on it in production.

---

### Verify OTP (login via OTP)
```
POST /auth/otp/verify
```
**Request body:**
```json
{
  "phone": "+919876543210",
  "code": "123456"
}
```

**Response `200`:** Same as Login response.

---

### Get My Profile
```
GET /auth/me
Authorization: Bearer <token>
```

**Response `200`:** `UserOut` object (same as register response).

---

### Update My Profile
```
PATCH /auth/me
Authorization: Bearer <token>
```
**Request body** (all fields optional):
```json
{
  "full_name": "Jane Doe",
  "email": "jane@example.com",
  "avatar_url": "https://cdn.example.com/avatar.jpg"
}
```

**Response `200`:** Updated `UserOut`.

---

### Change Password
```
POST /auth/me/change-password
Authorization: Bearer <token>
```
**Request body:**
```json
{
  "current_password": "OldPass1!",
  "new_password": "NewPass2@",
  "confirm_password": "NewPass2@"
}
```

**Response `200`:** Updated `UserOut`.

---

## 5. Categories

### List All Active Categories
```
GET /categories
```
Query params: `skip=0`, `limit=100`

**Response `200`:**
```json
[
  {
    "id": "uuid",
    "name": "Fresh Vegetables",
    "slug": "fresh-vegetables",
    "type": "VEGETABLE",
    "description": "Farm-fresh daily vegetables",
    "image_url": "https://cdn.example.com/vegetables.jpg",
    "is_active": true,
    "created_at": "...",
    "updated_at": "..."
  }
]
```

---

### Get Single Category
```
GET /categories/{category_id}
```

**Response `200`:** Single `CategoryOut` object.

---

## 6. Products

### List Products
```
GET /products
```
Query params:

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `category_id` | UUID | — | Filter by category |
| `search` | string | — | Text search on product name |
| `skip` | int | `0` | Pagination offset |
| `limit` | int | `30` | Max items (1–100) |

**Response `200`:**
```json
[
  {
    "id": "uuid",
    "name": "Tomatoes",
    "description": "Fresh red tomatoes",
    "price": 30.0,
    "stock": 100,
    "unit": "kg",
    "image_url": "https://cdn.example.com/tomato.jpg",
    "is_active": true,
    "is_out_of_stock": false,
    "category_id": "uuid",
    "created_at": "...",
    "updated_at": "..."
  }
]
```

---

### Get Product (flat)
```
GET /products/{product_id}
```

**Response `200`:** Single `ProductOut` (category as UUID only).

---

### Get Product Detail (with category)
```
GET /products/{product_id}/detail
```

**Response `200`:** `ProductDetailOut` — same as `ProductOut` but includes a nested `category` object:
```json
{
  "id": "uuid",
  "name": "Tomatoes",
  ...
  "category_id": "uuid",
  "category": {
    "id": "uuid",
    "name": "Fresh Vegetables",
    "slug": "fresh-vegetables",
    "type": "VEGETABLE",
    ...
  }
}
```

---

## 7. Cart

All cart endpoints require authentication.

### Get Cart
```
GET /cart
Authorization: Bearer <token>
```

**Response `200`:**
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "items": [
    {
      "id": "uuid",
      "product_id": "uuid",
      "quantity": 2,
      "unit_price": 30.0,
      "line_total": 60.0,
      "product": { ...ProductOut... },
      "created_at": "...",
      "updated_at": "..."
    }
  ],
  "subtotal": 60.0,
  "item_count": 2,
  "created_at": "...",
  "updated_at": "..."
}
```

---

### Add Item to Cart
```
POST /cart/items
Authorization: Bearer <token>
```
**Request body:**
```json
{
  "product_id": "uuid",
  "quantity": 1
}
```
- If the product is already in the cart, its quantity is **incremented** by the given amount.

**Response `201`:** Updated `CartOut`.

---

### Update Item Quantity
```
PUT /cart/items/{product_id}
Authorization: Bearer <token>
```
**Request body:**
```json
{
  "quantity": 3
}
```
- Sets the quantity to the **exact** value provided (replaces, not increments).

**Response `200`:** Updated `CartOut`.

---

### Remove Single Item
```
DELETE /cart/items/{product_id}
Authorization: Bearer <token>
```

**Response `200`:** Updated `CartOut` (item removed).

---

### Clear Entire Cart
```
DELETE /cart
Authorization: Bearer <token>
```

**Response `204 No Content`** — no body.

---

## 8. Orders

All order endpoints require authentication.

### Place Order
```
POST /orders
Authorization: Bearer <token>
```
**Request body:**
```json
{
  "delivery_address": "123 Main Street, Mumbai, Maharashtra 400001",
  "address_id": null,
  "notes": "Please call before delivery"
}
```
- `address_id` (optional): UUID of a saved address. If provided, overrides `delivery_address`.
- `notes` (optional): max 500 characters.

> **Important:** See [Business Rules](#11-business-rules) for delivery charge calculation and vegetable ordering time restriction.

**Response `201`:**
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "status": "placed",
  "subtotal": 120.0,
  "delivery_charge": 15.0,
  "total": 135.0,
  "delivery_address": "123 Main Street, Mumbai...",
  "notes": "Please call before delivery",
  "cancel_reason": null,
  "items": [
    {
      "id": "uuid",
      "product_id": "uuid",
      "quantity": 2,
      "unit_price": 30.0,
      "subtotal": 60.0,
      "created_at": "...",
      "updated_at": "..."
    }
  ],
  "tracking": [
    {
      "id": "uuid",
      "status": "placed",
      "description": "Order placed successfully",
      "changed_by": "system",
      "created_at": "...",
      "updated_at": "..."
    }
  ],
  "created_at": "...",
  "updated_at": "..."
}
```

---

### List My Orders
```
GET /orders
Authorization: Bearer <token>
```
Query params: `skip=0`, `limit=20`

**Response `200`:** Array of `OrderOut` objects (same shape as above).

---

### Get Single Order
```
GET /orders/{order_id}
Authorization: Bearer <token>
```

**Response `200`:** Single `OrderOut` with full `items` and `tracking` arrays.

---

## 9. Order Tracking

### Get Tracking Timeline (customer)
```
GET /orders/{order_id}/tracking
Authorization: Bearer <token>
```
Returns the status-change history for one of the authenticated user's own orders.

**Response `200`:**
```json
[
  {
    "id": "uuid",
    "status": "placed",
    "description": "Order placed successfully",
    "changed_by": "system",
    "created_at": "2026-03-10T09:00:00Z",
    "updated_at": "2026-03-10T09:00:00Z"
  },
  {
    "id": "uuid",
    "status": "confirmed",
    "description": "Your order has been confirmed",
    "changed_by": "admin-uuid",
    "created_at": "2026-03-10T09:15:00Z",
    "updated_at": "2026-03-10T09:15:00Z"
  }
]
```

---

## 10. Admin Panel

All admin endpoints require authentication **and** `is_admin: true` on the user. Regular users will receive `403 Forbidden`.

### Users

#### List All Users
```
GET /admin/users
Authorization: Bearer <admin_token>
```
Query params: `skip=0`, `limit=50`

**Response `200`:** Array of `UserOut`.

---

#### Update User Flags
```
PATCH /admin/users/{user_id}
Authorization: Bearer <admin_token>
```
**Request body** (all optional):
```json
{
  "is_active": true,
  "is_verified": true,
  "is_admin": false
}
```

**Response `200`:** Updated `UserOut`.

---

### Admin → Orders

#### List All Orders
```
GET /admin/orders
Authorization: Bearer <admin_token>
```
Query params: `skip=0`, `limit=50`

---

#### Get Any Order
```
GET /admin/orders/{order_id}
Authorization: Bearer <admin_token>
```

---

#### Update Order Status
```
PATCH /admin/orders/{order_id}/status
Authorization: Bearer <admin_token>
```
**Request body:**
```json
{
  "status": "confirmed",
  "description": "Order accepted and confirmed"
}
```
- `status`: one of `placed | confirmed | packed | out_for_delivery | delivered | cancelled`
- `description` (optional): note appended to tracking log

**Response `200`:** Updated `OrderOut`.

---

#### Cancel an Order
```
PATCH /admin/orders/{order_id}/cancel
Authorization: Bearer <admin_token>
```
**Request body:**
```json
{
  "reason": "Item out of stock unexpectedly"
}
```

**Response `200`:** Updated `OrderOut` with `status: cancelled` and `cancel_reason` populated.

---

#### Get Full Tracking for Any Order
```
GET /admin/orders/{order_id}/tracking
Authorization: Bearer <admin_token>
```

**Response `200`:** Array of `OrderTrackingOut` (same shape as customer tracking endpoint).

---

### Admin → Products

#### List Out-of-Stock Products
```
GET /admin/products/out-of-stock
Authorization: Bearer <admin_token>
```
Query params: `skip=0`, `limit=50`

**Response `200`:** Array of `ProductOut`.

---

#### Adjust Stock Level
```
POST /admin/products/{product_id}/adjust-stock
Authorization: Bearer <admin_token>
```
**Request body:**
```json
{
  "stock": 150
}
```
- Sets stock to the **absolute** value (not a delta/increment).

**Response `200`:** Updated `ProductOut`.

---

#### Create Product
```
POST /products
Authorization: Bearer <admin_token>
```
**Request body:**
```json
{
  "name": "Carrots",
  "description": "Fresh orange carrots",
  "price": 25.0,
  "stock": 200,
  "unit": "kg",
  "image_url": "https://cdn.example.com/carrot.jpg",
  "category_id": "uuid"
}
```

**Response `201`:** Created `ProductOut`.

---

#### Update Product
```
PATCH /products/{product_id}
Authorization: Bearer <admin_token>
```
**Request body** (all optional):
```json
{
  "name": "Updated Name",
  "price": 29.99,
  "is_active": false
}
```

**Response `200`:** Updated `ProductOut`.

---

### Admin → Offers

#### List Offers
```
GET /admin/offers
Authorization: Bearer <admin_token>
```

**Response `200`:**
```json
[
  {
    "id": "uuid",
    "product_id": "uuid",
    "title": "10% off Tomatoes",
    "discount_percent": 10.0,
    "max_uses": 100,
    "used_count": 23,
    "expires_at": "2026-04-01T00:00:00Z",
    "is_active": true,
    "created_at": "...",
    "updated_at": "..."
  }
]
```

---

#### Create Offer
```
POST /admin/offers
Authorization: Bearer <admin_token>
```
**Request body:**
```json
{
  "product_id": "uuid",
  "title": "Summer Sale - 15% off",
  "discount_percent": 15.0,
  "max_uses": 500,
  "expires_at": "2026-06-30T23:59:59Z"
}
```
- `max_uses`: omit or set to `null` for unlimited uses.

**Response `201`:** Created `OfferOut`.

---

#### Update Offer
```
PATCH /admin/offers/{offer_id}
Authorization: Bearer <admin_token>
```
**Request body** (all optional):
```json
{
  "title": "Extended Summer Sale",
  "expires_at": "2026-07-31T23:59:59Z"
}
```

**Response `200`:** Updated `OfferOut`.

---

#### Deactivate Offer
```
PATCH /admin/offers/{offer_id}/deactivate
Authorization: Bearer <admin_token>
```
No request body.

**Response `200`:** Updated `OfferOut` with `is_active: false`.

---

### Admin → Banners

#### List Banners
```
GET /admin/banners
Authorization: Bearer <admin_token>
```

**Response `200`:**
```json
[
  {
    "id": "uuid",
    "title": "Weekend Special",
    "image_url": "https://cdn.example.com/banner1.jpg",
    "link_url": "https://app.example.com/sale",
    "is_active": true,
    "sort_order": 0,
    "created_at": "...",
    "updated_at": "..."
  }
]
```

---

#### Create Banner
```
POST /admin/banners
Authorization: Bearer <admin_token>
```
**Request body:**
```json
{
  "title": "Weekend Special",
  "image_url": "https://cdn.example.com/banner1.jpg",
  "link_url": "https://app.example.com/sale",
  "sort_order": 0
}
```
- `link_url` is optional.
- Lower `sort_order` = shown first on the home screen.

**Response `201`:** Created `BannerOut`.

---

#### Update Banner
```
PATCH /admin/banners/{banner_id}
Authorization: Bearer <admin_token>
```
**Request body** (all optional):
```json
{
  "title": "New Title",
  "sort_order": 1,
  "is_active": false
}
```

---

#### Toggle Banner Active State
```
PATCH /admin/banners/{banner_id}/toggle
Authorization: Bearer <admin_token>
```
No request body. Flips `is_active` between `true` and `false`.

**Response `200`:** Updated `BannerOut`.

---

## 11. Business Rules

### Delivery Charge
| Cart Items | Delivery Charge |
|------------|----------------|
| 1 item | ₹10.00 |
| 2 or more items | ₹15.00 |

The `delivery_charge` field is always calculated server-side and returned in the order response. Never compute it on the frontend.

---

### Vegetable Ordering Time Window
- Orders containing products from the **VEGETABLE** category can **only be placed between 5:00 AM and 9:00 AM UTC**.
- Outside this window, placing an order with vegetable products will return a `400` error.
- **Tip:** Check the current UTC time and category type client-side to show the user a helpful message before they try to checkout.

---

### Offer / Discount Application
- Discounts are applied **per product** at order time if an active, non-expired offer exists for that product.
- `discount_percent` is the percentage off the `unit_price`.
- If `max_uses` is set and the offer has been used that many times, the discount is not applied.

---

## 12. React Integration Tips

### Axios Instance Setup

```js
// src/api/axios.js
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  headers: { 'Content-Type': 'application/json' },
});

// Attach access token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Auto-refresh on 401
api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const { data } = await axios.post('/api/v1/auth/refresh', {
          refresh_token: refreshToken,
        });
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('refresh_token', data.refresh_token);
        originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
        return api(originalRequest);
      } catch {
        // Refresh failed — redirect to login
        localStorage.clear();
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default api;
```

---

### Login & Store Tokens

```js
const login = async (phone, password) => {
  const { data } = await api.post('/auth/login', { phone, password });
  localStorage.setItem('access_token', data.access_token);
  localStorage.setItem('refresh_token', data.refresh_token);
};
```

---

### Fetch Products with Category Filter

```js
const getProducts = async (categoryId, search, page = 0) => {
  const params = { skip: page * 30, limit: 30 };
  if (categoryId) params.category_id = categoryId;
  if (search) params.search = search;
  const { data } = await api.get('/products', { params });
  return data; // array of ProductOut
};
```

---

### Add to Cart

```js
const addToCart = async (productId, quantity = 1) => {
  const { data } = await api.post('/cart/items', {
    product_id: productId,
    quantity,
  });
  return data; // CartOut
};
```

---

### Place an Order

```js
const checkout = async (deliveryAddress, notes = null) => {
  const { data } = await api.post('/orders', {
    delivery_address: deliveryAddress,
    notes,
  });
  return data; // OrderOut
};
```

---

### Check Vegetable Order Window (client-side hint)
```js
const isVegetableOrderAllowed = () => {
  const hour = new Date().getUTCHours(); // 0–23 UTC
  return hour >= 5 && hour < 9;
};

// Usage in checkout UI:
if (cartHasVegetables && !isVegetableOrderAllowed()) {
  alert('Vegetable orders can only be placed between 5 AM and 9 AM UTC');
}
```

---

### Order Status Display Map
```js
const ORDER_STATUS_LABELS = {
  placed:            { label: 'Order Placed',       color: 'blue'   },
  confirmed:         { label: 'Confirmed',           color: 'indigo' },
  packed:            { label: 'Packed',              color: 'purple' },
  out_for_delivery:  { label: 'Out for Delivery',    color: 'orange' },
  delivered:         { label: 'Delivered',           color: 'green'  },
  cancelled:         { label: 'Cancelled',           color: 'red'    },
};
```

---

### Pagination Pattern
```js
// Generic paginated fetch
const fetchPaginated = async (endpoint, page = 0, limit = 20, extraParams = {}) => {
  const { data } = await api.get(endpoint, {
    params: { skip: page * limit, limit, ...extraParams },
  });
  return data; // array — no wrapper object
};
```

> All list endpoints return a **plain array** — there is no `{ items, total }` wrapper. Determine end-of-list by checking `data.length < limit`.

---

*Document generated for API version 1.0 — March 2026*
