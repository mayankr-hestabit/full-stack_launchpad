# Query Engine Documentation

## Overview

The Query Engine is responsible for dynamically retrieving products from the database based on user-provided query parameters. Instead of creating multiple API endpoints for different operations such as searching, filtering, sorting, and pagination, a single endpoint is used to perform all these operations.

Endpoint:

GET /api/products

The query engine reads the request query parameters, constructs a MongoDB query object dynamically, and returns the matching products.

---

# Features Implemented

- Dynamic Search
- Category Filtering
- Price Range Filtering
- Dynamic Sorting
- Pagination
- Soft Delete Support

---

# 1. Dynamic Search

## Purpose

Allows users to search products using a keyword.

The search is performed on multiple fields:

- Product Name
- Product Category

MongoDB uses the `$or` operator along with regular expressions (`$regex`) to perform a case-insensitive search.

Example Request

GET /api/products?search=iphone

Generated MongoDB Filter

```javascript
{
    $or: [
        {
            name: {
                $regex: "iphone",
                $options: "i"
            }
        },
        {
            category: {
                $regex: "iphone",
                $options: "i"
            }
        }
    ]
}
```

Explanation

- `$regex` performs pattern matching.
- `$options: "i"` makes the search case-insensitive.
- `$or` means either the product name or category can match.

---

# 2. Category Filtering

## Purpose

Allows users to retrieve products belonging to a specific category.

Example Request

GET /api/products?category=Electronics

Generated Filter

```javascript
{
    category: "Electronics"
}
```

Unlike search, category filtering performs an exact match.

---

# 3. Price Range Filtering

## Purpose

Retrieve products within a given price range.

Supported Parameters

- minPrice
- maxPrice

Example

GET /api/products?minPrice=500&maxPrice=1000

Generated Filter

```javascript
{
    price: {
        $gte: 500,
        $lte: 1000
    }
}
```

Explanation

- `$gte` = Greater Than or Equal To
- `$lte` = Less Than or Equal To

The spread operator is used while constructing the filter so that both conditions can exist together.

```javascript
filter.price = {
    ...filter.price,
    $gte: Number(queryParams.minPrice)
};

filter.price = {
    ...filter.price,
    $lte: Number(queryParams.maxPrice)
};
```

---

# 4. Combining Search and Filters

All filters are combined into a single MongoDB query object.

Example Request

GET /api/products?search=iphone&category=Mobile&minPrice=500&maxPrice=1000

Generated Query

```javascript
{
    $or: [
        {
            name: {
                $regex: "iphone",
                $options: "i"
            }
        },
        {
            category: {
                $regex: "iphone",
                $options: "i"
            }
        }
    ],

    category: "Mobile",

    price: {
        $gte: 500,
        $lte: 1000
    }
}
```

MongoDB interprets this as

```
(Name contains "iphone"
OR
Category contains "iphone")

AND

Category = "Mobile"

AND

Price >= 500

AND

Price <= 1000
```

---

# 5. Dynamic Sorting

## Purpose

Allows users to sort products by any field.

Supported Format

GET /api/products?sort=price:asc

or

GET /api/products?sort=price:desc

Implementation

```javascript
const [field, order] = queryParams.sort.split(":");

sort[field] = order === "desc" ? -1 : 1;
```

Generated Sort Object

Ascending

```javascript
{
    price: 1
}
```

Descending

```javascript
{
    price: -1
}
```

MongoDB Query

```javascript
Product.find(filter).sort(sort);
```

---

# 6. Pagination

## Purpose

Instead of returning every product from the database, pagination returns a limited number of products.

Supported Parameters

- page
- limit

Example

GET /api/products?page=2&limit=5

Pagination Formula

```javascript
skip = (page - 1) * limit;
```

Implementation

```javascript
const page = Number(queryParams.page) || 1;

const limit = Number(queryParams.limit) || 10;

const skip = (page - 1) * limit;
```

MongoDB Query

```javascript
Product.find(filter)
    .sort(sort)
    .skip(skip)
    .limit(limit);
```

Example

Database contains 25 products.

Request

```
?page=2&limit=5
```

MongoDB performs

```
skip(5)
limit(5)
```

Returned Products

```
6
7
8
9
10
```

---

# 7. Soft Delete Support

Instead of permanently removing a product from the database, the application marks it as deleted.

Schema

```javascript
isDeleted: {
    type: Boolean,
    default: false
}
```

Delete Operation

Instead of

```javascript
findByIdAndDelete(id)
```

the application performs

```javascript
findByIdAndUpdate(id, {
    isDeleted: true
});
```

To prevent deleted products from appearing in normal requests, every query automatically includes

```javascript
filter.isDeleted = false;
```

As a result

```
Deleted products remain inside the database but are hidden from API responses.
```

---

# Repository Layer

The repository receives the generated query objects from the service layer.

```javascript
Product.find(filter)
       .sort(sort)
       .skip(skip)
       .limit(limit);
```

Responsibilities

- Execute MongoDB query
- Apply sorting
- Apply pagination
- Return results

---

# Service Layer

The service layer is responsible for

- Reading query parameters
- Building MongoDB filter objects
- Building sort objects
- Calculating pagination
- Calling the repository layer

This keeps controllers lightweight and separates business logic from database operations.

---

# Architecture Flow

```
Client Request
      │
      ▼
Controller
      │
      ▼
Service Layer
      │
      ├── Build Filter
      ├── Build Sort
      ├── Calculate Pagination
      ▼
Repository Layer
      │
      ▼
MongoDB
      │
      ▼
JSON Response
```

---

# Benefits

- Single API endpoint handles multiple use cases.
- Cleaner and reusable code.
- Easy to extend with new filters.
- Better performance through pagination.
- Supports flexible searching.
- Implements soft delete without losing data.
- Follows layered architecture (Controller → Service → Repository).

---

# Example API

```
GET /api/products?search=iphone&category=Mobile&minPrice=500&maxPrice=1000&sort=price:desc&page=2&limit=5
```

Execution Flow

1. Search products containing "iphone".
2. Filter category to "Mobile".
3. Filter products priced between 500 and 1000.
4. Sort by price in descending order.
5. Skip the first page.
6. Return only five products.

The query engine dynamically combines all requested operations into a single MongoDB query, providing an efficient and scalable API.