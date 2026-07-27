# Week 4 Advanced Backend - Architecture

## Overview

This project follows a layered architecture to keep the code modular, scalable, and maintainable. Each layer has a single responsibility, making the application easier to understand, test, and extend.

---

## Project Structure

```
week4-advanced-backend/
│
├── src/
│   ├── config/
│   ├── loaders/
│   ├── controllers/
│   ├── services/
│   ├── repositories/
│   ├── models/
│   ├── routes/
│   ├── middlewares/
│   ├── utils/
│   └── jobs/
│
├── logs/
├── server.js
├── package.json
├── .env.local
├── .env.dev
├── .env.prod
└── ARCHITECTURE.md
```

---

# Folder Responsibilities

## config/

Stores application configuration such as:

- PORT
- MongoDB URI
- Environment variables
- JWT Secret (future)

---

## loaders/

Responsible for initializing different parts of the application.

Examples:

- Express Loader
- Database Loader

---

## controllers/

Handles incoming HTTP requests and sends responses.

Controllers should not contain business logic.

---

## services/

Contains business logic.

Examples:

- Authentication
- Product validation
- Discount calculation
- Order processing

---

## repositories/

Responsible only for database operations.

Examples:

- Create User
- Find User
- Update Product
- Delete Order

---

## models/

Defines MongoDB schemas using Mongoose.

Examples:

- User
- Product
- Order

---

## routes/

Maps API endpoints to controllers.

Example:

GET /users

↓

User Controller

---

## middlewares/

Executes before controllers.

Examples:

- Authentication
- Validation
- Logging
- Rate Limiting

---

## utils/

Reusable helper functions.

Examples:

- Logger
- JWT Helper
- Date Formatter

---

## jobs/

Background tasks.

Examples:

- Email Notifications
- Report Generation

---

## logs/

Stores application logs.

Examples:

- Server Started
- Database Connected
- Errors

---

# Startup Flow

```
npm run dev
        │
        ▼
server.js
        │
        ▼
Load Environment Variables
        │
        ▼
Create Express Application
        │
        ▼
Load Middlewares
        │
        ▼
Load Routes
        │
        ▼
Connect MongoDB
        │
        ▼
Start Server
        │
        ▼
Ready to Accept Requests
```

---

# Request Flow

```
Client
   │
   ▼
Route
   │
   ▼
Controller
   │
   ▼
Service
   │
   ▼
Repository
   │
   ▼
MongoDB
   │
   ▼
Repository
   │
   ▼
Service
   │
   ▼
Controller
   │
   ▼
JSON Response
```

---

# Design Principles

- Layered Architecture
- Separation of Concerns
- Single Responsibility Principle (SRP)
- Modular Design
- Environment-based Configuration
- Production-ready Logging

---

# Technologies Used

- Node.js
- Express.js
- MongoDB
- Mongoose
- Dotenv
- Pino Logger