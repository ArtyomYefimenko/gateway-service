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

- `/auth/api/v1/...` → Auth Service
- `/products/api/v1/...` → Product Service
- `/orders/api/v1/...` → Order Service
- `/payments/callback/...` → Payment Service

The gateway trims service-specific prefixes before forwarding requests, so internal services keep clean `/api/v1/...` routes.

## API Documentation

API documentation for each internal service is available via the `/docs` endpoint by choosing the required service.

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

To start the services locally, navigate to the `infrastructure` directory and run:

```bash
make run
