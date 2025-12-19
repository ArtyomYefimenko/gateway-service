# Gateway Service

Gateway Service is the single entry point (API Gateway) for the Microshop system.  
It routes external client requests to internal microservices and provides a unified API for the frontend.

## Responsibilities

- Acts as an **API Gateway** for all backend services
- Proxies requests to:
  - Product Service
  - Order Service
  - Payment Service
  - Auth Service
- Centralized request routing and URL normalization
- Shared HTTP connection pooling for downstream services
- Authentication token forwarding (e.g. JWT)

## API Design

The gateway exposes a clean and consistent public API.  
Internally, requests are proxied to the corresponding microservices.

## Routing Examples

- `/products/api/v1/...` → Product Service
- `/orders/api/v1/...` → Order Service
- `/payments/api/v1/...` → Payment Service
- `/auth/api/v1/...` → Auth Service

The gateway trims service-specific prefixes before forwarding requests, so internal services keep clean `/api/v1/...` routes.

## API Documentation

API documentation for each internal service is also available via Gateway endpoints:

- `/products/docs` – Product Service API documentation
- `/orders/docs` – Order Service API documentation
- `/payments/docs` – Payment Service API documentation
- `/auth/docs` – Auth Service API documentation

## Tech Stack

- **Python 3.13**
- **FastAPI**
- **aiohttp** for async HTTP proxying
- **Pydantic** for data validation
- **Docker**

## Connection Pooling

A shared `aiohttp.ClientSession` is created on application startup:

- Reused across all outgoing requests
- Configured with connection pooling
- Improves performance and avoids creating a new connection per request

The session is gracefully closed on application shutdown.

## Health Check

- `GET /health` – Gateway health endpoint

## Running Locally

```bash
# Inside infrastructure folder
docker-compose up
