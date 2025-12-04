# Order Management System

## Overview

This project implements an **Order Management System** using a microservices architecture. The system consists of three independent services: **Order Service**, **Inventory Service**, and **Payment Service**. Each service has its own database and communicates via REST APIs. Docker and Docker Compose are used to containerize and orchestrate the services.

## Prerequisites

* Python 3.x
* Docker

## Running the System

1. Clone the repository:

```bash
git clone https://github.com/MasoomehMokhtari78/order-system-microservices
cd order-system-microservices
```

2. Build and start all services:

```bash
docker compose up --build
```

This will:

* Build Docker images for all services
* Start PostgreSQL databases for each service
* Launch services on their respective ports

| Service           | Port |
| ----------------- | ---- |
| Order Service     | 8001 |
| Inventory Service | 8002 |
| Payment Service   | 8003 |

3. Verify each service is running using the health endpoint:

```bash
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
```

Expected response:

```json
{"status": "ok"}
```

## Service Descriptions, Endpoint Examples, and Swagger UI

### 1. Inventory Service

**Responsibilities:**

* Manage products and stock levels
* Reserve and release stock

**Swagger UI:** `http://localhost:8002/docs`

**Endpoints and Examples:**

* `POST /api/v1/stock/items` — Add or update a stock item

```json
POST /api/v1/stock/items
{
  "item_sku": "SKU-ABC",
  "quantity": 10
}
```

Response:

```json
{
  "item_sku": "SKU-ABC",
  "quantity": 10
}
```

* `GET /api/v1/stock/` — List all items

```json
GET /api/v1/stock/
```

Response:

```json
[
  {"item_sku": "SKU-ABC", "quantity": 10},
  {"item_sku": "SKU-XYZ", "quantity": 5}
]
```

* `GET /api/v1/stock/{sku}` — Get stock for a specific item

```json
GET /api/v1/stock/SKU-ABC
```

Response:

```json
{
  "item_sku": "SKU-ABC",
  "quantity": 10
}
```

* `POST /api/v1/stock/reserve` — Reserve stock

```json
POST /api/v1/stock/reserve
{
  "item_sku": "SKU-ABC",
  "quantity": 2
}
```

Response:

```json
{
  "reservation_id": 1,
  "item_sku": "SKU-ABC",
  "quantity": 2,
  "remaining_quantity": 8
}
```

* `POST /api/v1/stock/release` — Release reserved stock

```json
POST /api/v1/stock/release
{
  "reservation_id": 1
}
```

Response:

```json
{
  "released": true,
  "reservation_id": 1,
  "item_sku": "SKU-ABC"
}
```

### 2. Payment Service

**Responsibilities:**

* Simulate payment transactions
* Approve or decline payments based on amount

**Swagger UI:** `http://localhost:8003/docs`

**Endpoint and Example:**

* `POST /api/v1/payments/authorize` — Authorize a payment

```json
POST /api/v1/payments/authorize
{
  "order_id": 1,
  "amount": 200.50,
  "currency": "USD"
}
```

Response:

```json
{
  "authorized": true,
  "payment_id": 1
}
```

### 3. Order Service

**Responsibilities:**

* Receive new orders
* Reserve stock via Inventory Service
* Process payments via Payment Service
* Confirm or fail orders based on stock and payment status
* Handle idempotency using `idempotency_key`

**Swagger UI:** `http://localhost:8001/docs`

**Endpoints and Examples:**

* `POST /api/v1/orders/` — Create a new order

```json
POST /api/v1/orders/
{
  "item_sku": "SKU-ABC",
  "quantity": 2,
  "amount": 200,
  "currency": "USD",
  "idempotency_key": "unique-key-001"
}
```

Response:

```json
{
  "order_id": 1,
  "status": "CONFIRMED",
  "payment_status": "SUCCEEDED",
  "item_sku": "SKU-ABC",
  "quantity": 2,
  "amount": 200,
  "currency": "USD"
}
```

* `GET /api/v1/orders/` — List all orders

```json
GET /api/v1/orders/
```

Response:

```json
[
  {
    "order_id": 1,
    "status": "CONFIRMED",
    "payment_status": "SUCCEEDED",
    "item_sku": "SKU-ABC",
    "quantity": 2,
    "amount": 200,
    "currency": "USD"
  }
]
```

* `GET /api/v1/orders/{id}` — Get order details

```json
GET /api/v1/orders/1
```

Response:

```json
{
  "order_id": 1,
  "status": "CONFIRMED",
  "payment_status": "SUCCEEDED",
  "item_sku": "SKU-ABC",
  "quantity": 2,
  "amount": 200,
  "currency": "USD"
}
```
