# Week 4 Advanced Backend — API Documentation

## 1. Overview

This document describes the REST APIs of the Week 4 Advanced Backend application.

### Tech Stack

* Node.js
* Express.js
* MongoDB
* Mongoose
* Pino
* Zod validation
* Helmet
* CORS
* Rate Limiting

### Architecture

```text
Client
  ↓
Routes
  ↓
Validation / Middleware
  ↓
Controller
  ↓
Service
  ↓
Repository
  ↓
MongoDB
```

The application follows separation of concerns by keeping routing, validation, controllers, business logic, and database operations in separate layers.

---

# 2. Base URL

Recommended API base URL:

```text
http://localhost:5000/api
```

The application currently mounts routes at both `/` and `/api`, but `/api` is recommended for API usage.

---

# 3. Common Response Format

### Success

```json
{
  "success": true,
  "data": {}
}
```

### Collection Response

```json
{
  "success": true,
  "count": 2,
  "data": []
}
```

### Error

Errors are passed to the centralized global error handler using:

```js
next(error);
```

The global error middleware is responsible for producing standardized error responses.

---

# 4. System APIs

## 4.1 Home

### GET `/api/`

Returns a welcome message.

### Example

```http
GET http://localhost:5000/api/
```

### Response

```json
{
  "success": true,
  "message": "Welcome to Week 4 Advanced Backend 🚀",
  "author": "Mayank Raj"
}
```

### Status

```text
200 OK
```

---

## 4.2 Health Check

### GET `/api/health`

Checks whether the server is healthy.

### Example

```http
GET http://localhost:5000/api/health
```

### Response

```json
{
  "success": true,
  "status": "Server is healthy ✅"
}
```

### Status

```text
200 OK
```

---

# 5. User APIs

Base path:

```text
/api/users
```

---

## 5.1 Create User

### POST `/api/users`

Creates a new user.

### Request

```http
POST /api/users
Content-Type: application/json
```

Example:

```json
{
  "name": "Mayank Raj",
  "email": "mayank@example.com",
  "password": "password123",
  "age": 22
}
```

The request is validated using:

```text
createUserSchema
```

### Success

```json
{
  "success": true,
  "data": {}
}
```

### Status Codes

```text
201 Created
400 Bad Request
500 Internal Server Error
```

---

## 5.2 Get Users

### GET `/api/users`

Returns all users.

### Example

```http
GET /api/users
```

### Response

```json
{
  "success": true,
  "data": []
}
```

### Status Codes

```text
200 OK
500 Internal Server Error
```

---

## 5.3 Get User By ID

### GET `/api/users/:id`

Returns a user using their MongoDB ID.

### Example

```http
GET /api/users/64f123456789abcdef123456
```

### Path Parameter

| Parameter | Description     |
| --------- | --------------- |
| `id`      | MongoDB user ID |

### Success

```json
{
  "success": true,
  "data": {}
}
```

### Status Codes

```text
200 OK
404 Not Found
500 Internal Server Error
```

---

## 5.4 Update User

### PUT `/api/users/:id`

Updates an existing user.

### Example

```http
PUT /api/users/64f123456789abcdef123456
Content-Type: application/json
```

```json
{
  "name": "Mayank Raj Updated",
  "age": 23
}
```

Validation:

```text
updateUserSchema
```

### Status Codes

```text
200 OK
400 Bad Request
404 Not Found
500 Internal Server Error
```

---

## 5.5 Delete User

### DELETE `/api/users/:id`

Deletes a user using their ID.

### Example

```http
DELETE /api/users/64f123456789abcdef123456
```

### Status Codes

```text
200 OK
404 Not Found
500 Internal Server Error
```

---

# 6. Product APIs

Base path:

```text
/api/products
```

### Product Endpoints

| Method | Endpoint            | Description                     |
| ------ | ------------------- | ------------------------------- |
| POST   | `/api/products`     | Create product                  |
| GET    | `/api/products`     | Get/search/filter/sort products |
| GET    | `/api/products/:id` | Get product by ID               |
| PATCH  | `/api/products/:id` | Update product                  |
| DELETE | `/api/products/:id` | Soft-delete product             |

---

# 7. Create Product

### POST `/api/products`

Creates a new product.

### Request

```http
POST /api/products
Content-Type: application/json
```

Example:

```json
{
  "name": "Bellavita Perfume",
  "description": "Light fragrance elegant perfume for men",
  "category": "Men",
  "price": 999
}
```

The request is validated using:

```text
createProductSchema
```

### Flow

```text
POST /products
   ↓
Validation
   ↓
Controller
   ↓
Service
   ↓
Repository
   ↓
MongoDB
```

### Success

```json
{
  "success": true,
  "data": {}
}
```

### Status Codes

```text
201 Created
400 Bad Request
500 Internal Server Error
```

---

# 8. Get Products

### GET `/api/products`

Returns products with support for:

* Searching
* Category filtering
* Price filtering
* Sorting
* Pagination
* Soft-delete exclusion

### Basic Request

```http
GET /api/products
```

### Response

```json
{
  "success": true,
  "count": 2,
  "data": []
}
```

---

# 9. Product Search

The `search` parameter searches both:

```text
name
category
```

The search is case-insensitive.

### Example

```http
GET /api/products?search=perfume
```

Internally, the service uses:

```js
{
  $or: [
    {
      name: {
        $regex: queryParams.search,
        $options: "i"
      }
    },
    {
      category: {
        $regex: queryParams.search,
        $options: "i"
      }
    }
  ]
}
```

Therefore:

```text
perfume
Perfume
PERFUME
```

can match the same product.

---

# 10. Category Filtering

Use:

```text
category
```

to filter products by category.

### Example

```http
GET /api/products?category=Men
```

The service adds:

```js
{
  category: "Men"
}
```

to the query filter.

---

# 11. Price Filtering

## Minimum Price

```http
GET /api/products?minPrice=500
```

Equivalent condition:

```js
{
  price: {
    $gte: 500
  }
}
```

## Maximum Price

```http
GET /api/products?maxPrice=2000
```

Equivalent condition:

```js
{
  price: {
    $lte: 2000
  }
}
```

## Price Range

Both can be combined:

```http
GET /api/products?minPrice=500&maxPrice=2000
```

Equivalent condition:

```js
{
  price: {
    $gte: 500,
    $lte: 2000
  }
}
```

---

# 12. Product Sorting

Products can be sorted using:

```text
sort=field:order
```

Format:

```text
sort=<field>:<order>
```

### Ascending

```http
GET /api/products?sort=price:asc
```

### Descending

```http
GET /api/products?sort=price:desc
```

### Examples

```http
GET /api/products?sort=name:asc
GET /api/products?sort=name:desc
GET /api/products?sort=price:asc
GET /api/products?sort=price:desc
```

The implementation creates a MongoDB sort object:

```js
const [field, order] = queryParams.sort.split(":");

sort[field] = order === "desc" ? -1 : 1;
```

Therefore:

```text
asc  → 1
desc → -1
```

---

# 13. Product Pagination

Pagination uses:

```text
page
limit
```

### Example

```http
GET /api/products?page=1&limit=10
```

Default values:

```text
page  = 1
limit = 10
```

The skip value is calculated as:

```text
skip = (page - 1) × limit
```

Example:

```text
page = 2
limit = 10

skip = (2 - 1) × 10
     = 10
```

The repository receives:

```text
filter
sort
skip
limit
```

and performs the MongoDB query.

---

# 14. Combined Query

Search, filters, sorting, and pagination can be combined.

### Example

```http
GET /api/products?search=perfume&category=Men&minPrice=500&maxPrice=2000&sort=price:desc&page=1&limit=10
```

This query means:

```text
Search:
    perfume

Search fields:
    name OR category

Category:
    Men

Price:
    >= 500
    <= 2000

Sorting:
    price descending

Page:
    1

Limit:
    10
```

### Query Processing

```text
Request
   ↓
Read Query Parameters
   ↓
Build Filter
   ↓
Apply Search
   ↓
Apply Category
   ↓
Apply Price Range
   ↓
Apply Sorting
   ↓
Calculate Pagination
   ↓
MongoDB
   ↓
Return Products
```

---

# 15. Product Query Reference

| Feature         | Example                                                                                   |
| --------------- | ----------------------------------------------------------------------------------------- |
| Search          | `?search=perfume`                                                                         |
| Category        | `?category=Men`                                                                           |
| Min price       | `?minPrice=500`                                                                           |
| Max price       | `?maxPrice=2000`                                                                          |
| Price range     | `?minPrice=500&maxPrice=2000`                                                             |
| Sort ascending  | `?sort=price:asc`                                                                         |
| Sort descending | `?sort=price:desc`                                                                        |
| Page            | `?page=2`                                                                                 |
| Limit           | `?limit=10`                                                                               |
| Search + sort   | `?search=perfume&sort=price:desc`                                                         |
| Full query      | `?search=perfume&category=Men&minPrice=500&maxPrice=2000&sort=price:desc&page=1&limit=10` |

---

# 16. Get Product By ID

### GET `/api/products/:id`

Returns a product using its MongoDB ID.

### Example

```http
GET /api/products/6a69fcd3c305c5ab1dc50ad6
```

### Path Parameter

| Parameter | Description        |
| --------- | ------------------ |
| `id`      | MongoDB product ID |

### Success

```json
{
  "success": true,
  "data": {}
}
```

### Not Found

```json
{
  "success": false,
  "message": "Product not found"
}
```

### Status Codes

```text
200 OK
404 Not Found
500 Internal Server Error
```

---

# 17. Update Product

### PATCH `/api/products/:id`

Partially updates a product.

### Example

```http
PATCH /api/products/6a69fcd3c305c5ab1dc50ad6
Content-Type: application/json
```

```json
{
  "price": 1199
}
```

Validation:

```text
updateProductSchema
```

### Success

```json
{
  "success": true,
  "data": {}
}
```

### Status Codes

```text
200 OK
400 Bad Request
404 Not Found
500 Internal Server Error
```

---

# 18. Delete Product

### DELETE `/api/products/:id`

Deletes a product using the product ID.

The application uses **soft deletion**, meaning the product remains in the database but is marked as deleted.

### Example

```http
DELETE /api/products/6a69fcd3c305c5ab1dc50ad6
```

### Success

```json
{
  "success": true,
  "message": "Product deleted successfully",
  "data": {}
}
```

### Status Codes

```text
200 OK
404 Not Found
500 Internal Server Error
```

---

# 19. Soft Delete

Product queries automatically apply:

```js
filter.isDeleted = false;
```

Therefore normal product listing only returns products where:

```text
isDeleted = false
```

A deleted product is not physically removed from MongoDB.

```text
DELETE Product
      ↓
Mark as Deleted
      ↓
isDeleted = true
      ↓
Excluded from GET /products
```

---

# 20. Validation

Validation is implemented through reusable middleware:

```text
middlewares/validate.js
```

Validation schemas are separated from controllers.

```text
validations/
├── user.validation.js
└── product.validation.js
```

### Validated APIs

| API                   | Schema                |
| --------------------- | --------------------- |
| POST `/users`         | `createUserSchema`    |
| PUT `/users/:id`      | `updateUserSchema`    |
| POST `/products`      | `createProductSchema` |
| PATCH `/products/:id` | `updateProductSchema` |

Invalid data is rejected before reaching the controller.

---

# 21. Request Tracing

The application uses request tracing middleware:

```js
app.use(requestTracing);
```

Each request receives a unique `requestId`.

The ID is available throughout the request lifecycle:

```text
Request
   ↓
requestId
   ↓
Controller
   ↓
Service
   ↓
Repository
```

Example:

```text
be2b62f7-ce45-4f7b-870f-76c305f0ebdb
```

This makes it possible to trace one request across all backend layers.

---

# 22. Logging

Logging is implemented using **Pino**.

Log file:

```text
logs/app.log
```

Example:

```json
{
  "level": 30,
  "time": 1785837190527,
  "pid": 61122,
  "hostname": "Mac",
  "requestId": "be2b62f7-ce45-4f7b-870f-76c305f0ebdb",
  "msg": "Getting products"
}
```

The same `requestId` is used across controller and service logs.

Example request flow:

```text
Getting products
        ↓
Product service: getting products
        ↓
Product service: products fetched successfully
        ↓
Products fetched successfully
```

This provides structured and traceable application logging.

---

# 23. Security Middleware

The application applies security middleware globally.

### Helmet

Adds security-related HTTP headers.

### CORS

Controls cross-origin requests.

### Rate Limiter

Limits excessive requests.

The middleware order is:

```text
Helmet
  ↓
CORS
  ↓
Rate Limiter
  ↓
JSON Parser
  ↓
Request Tracing
  ↓
Routes
```

---

# 24. JSON Body Limit

The application limits JSON request bodies to:

```text
10 KB
```

Configuration:

```js
app.use(express.json({ limit: "10kb" }));
```

This helps prevent unnecessarily large JSON payloads.

---

# 25. Global Error Handling

The application uses centralized error handling:

```js
app.use(errorHandler);
```

Controllers catch errors and pass them to the middleware:

```js
try {
  // operation
} catch (error) {
  next(error);
}
```

### Flow

```text
Request
   ↓
Controller
   ↓
Error
   ↓
next(error)
   ↓
Global Error Handler
   ↓
Standardized Response
```

This prevents duplicated error-handling logic across controllers.

---

# 26. Complete API Reference

## System

| Method | Endpoint      | Description     |
| ------ | ------------- | --------------- |
| GET    | `/api/`       | Welcome message |
| GET    | `/api/health` | Health check    |

## Users

| Method | Endpoint         | Description   |
| ------ | ---------------- | ------------- |
| POST   | `/api/users`     | Create user   |
| GET    | `/api/users`     | Get all users |
| GET    | `/api/users/:id` | Get user      |
| PUT    | `/api/users/:id` | Update user   |
| DELETE | `/api/users/:id` | Delete user   |

## Products

| Method | Endpoint            | Description                          |
| ------ | ------------------- | ------------------------------------ |
| POST   | `/api/products`     | Create product                       |
| GET    | `/api/products`     | Search/filter/sort/paginate products |
| GET    | `/api/products/:id` | Get product                          |
| PATCH  | `/api/products/:id` | Update product                       |
| DELETE | `/api/products/:id` | Soft-delete product                  |

---

# 27. Testing Examples

### Health Check

```bash
curl http://localhost:5000/api/health
```

### Get Products

```bash
curl http://localhost:5000/api/products
```

### Search

```bash
curl "http://localhost:5000/api/products?search=perfume"
```

### Filter and Sort

```bash
curl "http://localhost:5000/api/products?category=Men&sort=price:desc"
```

### Pagination

```bash
curl "http://localhost:5000/api/products?page=2&limit=5"
```

### Full Query

```bash
curl "http://localhost:5000/api/products?search=perfume&category=Men&minPrice=500&maxPrice=2000&sort=price:desc&page=1&limit=10"
```

---

# 28. Final Architecture

```text
                    Client
                      │
                      ▼
                 Express App
                      │
        ┌─────────────┴─────────────┐
        │                           │
 Security Middleware          Request Tracing
        │                           │
        └─────────────┬─────────────┘
                      ▼
                    Routes
                      │
                      ▼
                 Validation
                      │
                      ▼
                 Controllers
                      │
                      ▼
                   Services
                      │
                      ▼
                 Repositories
                      │
                      ▼
                   MongoDB

Supporting Components:
──────────────────────
• Global Error Handler
• Pino Logger
• Request ID Tracking
• Helmet
• CORS
• Rate Limiting
• Search
• Filtering
• Sorting
• Pagination
• Soft Delete
```

The backend provides a modular REST API with centralized validation, error handling, security middleware, request tracing, structured logging, CRUD operations, soft deletion, and a flexible product query engine supporting search, filtering, sorting, and pagination.