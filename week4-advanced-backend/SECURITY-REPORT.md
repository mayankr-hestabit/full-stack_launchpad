# Security Test Report

## Week 4 — Day 4

**Project:** Advanced Backend API
**Technology:** Node.js, Express.js, MongoDB, Mongoose
**Testing Tools:** Postman, Node.js Terminal

---

## 1. NoSQL Injection Test

### Objective

To verify that the API does not allow malicious MongoDB operators to manipulate database queries.

Since the application uses MongoDB, this is a NoSQL Injection test.

### Testing Tool

Postman

### Test Input

The following malicious MongoDB operator payload was tested:

```json
{
  "email": {
    "$ne": null
  }
}
```

The `$ne` operator was used to check whether user-controlled input could be interpreted as a MongoDB query operator.

### Expected Result

The API should not allow user input to manipulate MongoDB queries.

Malicious MongoDB operators should be rejected or safely handled.

### Actual Result

The payload was tested through Postman.

The API did not allow the tested MongoDB operator to manipulate the database query.

### Result

PASS

### Conclusion

The NoSQL Injection test was successfully performed. The tested MongoDB operator was not able to manipulate the database query.

---

## 2. Rate Limiting Test

### Objective

To verify that the API prevents excessive repeated requests from the same client.

### Configuration

The rate limiter was configured with:

```javascript
windowMs: 15 * 60 * 1000,
max: 100,
standardHeaders: true,
legacyHeaders: false,
```

This allows a maximum of 100 requests within a 15-minute window.

### Testing Tool

Node.js Terminal

### Test Endpoint

```text
GET http://localhost:5000/api/health
```

### Test Program

The following Node.js `while` loop was used to send 110 requests:

```javascript
let i = 0;

while (i < 110) {
  const response = await fetch("http://localhost:5000/api/health");

  console.log(
    `Request ${i + 1}: ${response.status} ${response.statusText}`
  );

  i++;
}
```

### Expected Result

The first 100 requests should be accepted.

Requests after the configured limit should return:

```text
429 Too Many Requests
```

### Expected Response

```json
{
  "success": false,
  "message": "Too many requests. Please try again later."
}
```

### Result

PASS

### Conclusion

The rate-limiting mechanism was tested by sending more than 100 requests using the Node.js `while` loop. Requests exceeding the configured limit were handled by the rate limiter.

---

## 3. Payload Size Limiting Test

### Objective

To verify that the API rejects request bodies that exceed the configured maximum payload size.

### Configuration

The Express JSON parser was configured as:

```javascript
app.use(express.json({ limit: "10kb" }));
```

This limits JSON request bodies to 10 KB.

### Testing Tool

Postman

### Test Method

A JSON request body larger than 10 KB was sent to the API.

For example, a product request containing a very large `description` field can be used to exceed the configured limit.

### Expected Result

The API should reject the request before it reaches the controller.

Expected HTTP status:

```text
413 Payload Too Large
```

### Result

PASS

### Conclusion

The payload size limit prevents excessively large JSON request bodies from being processed by the application.

---

## 4. Zod Validation Test

### Objective

To verify that invalid request data is rejected before reaching the controller and database layer.

### Testing Tool

Postman

### Example Invalid User Request

```json
{
  "name": "",
  "email": "invalid-email",
  "password": "123"
}
```

### Expected Result

The request should be rejected because:

* `name` is empty.
* `email` is not a valid email address.
* `password` does not meet the minimum length requirement.

The request should not proceed to the controller or database.

### Validation Flow

```text
Client Request
      |
      v
Zod Validation
      |
      v
Invalid Input
      |
      v
Validation Error
      |
      X
Controller is not executed
```

### Result

PASS

### Conclusion

Zod validation successfully prevents invalid request data from reaching the controller and database layers.

---

# 5. Security Test Summary

| Test                  | Tool             | Expected Result                            | Result |
| --------------------- | ---------------- | ------------------------------------------ | ------ |
| NoSQL Injection       | Postman          | Malicious MongoDB operators safely handled | PASS   |
| Rate Limiting         | Node.js Terminal | Requests beyond limit return 429           | PASS   |
| Payload Size Limiting | Postman          | Payloads over 10 KB rejected               | PASS   |
| Zod Validation        | Postman          | Invalid input rejected before controller   | PASS   |

---

# 6. Overall Conclusion

Four major security and hardening mechanisms were manually tested in the Week 4 Day 4 backend project.

The tests covered:

1. NoSQL Injection
2. Rate Limiting
3. Payload Size Limiting
4. Zod Request Validation

Testing was performed using Postman and the Node.js terminal. The implemented security mechanisms were verified according to their configured behavior and provide protection against malicious database input, excessive requests, oversized request bodies, and invalid application data.
