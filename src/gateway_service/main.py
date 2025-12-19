import logging
from contextlib import asynccontextmanager

import aiohttp
from fastapi import (
    APIRouter,
    FastAPI,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from gateway_service.api.docs import router as docs_router
from gateway_service.api.health import router as health_router
from gateway_service.api.services import router as services_router
from gateway_service.config import settings
from gateway_service.services import (
    AuthService,
    OrderService,
    PaymentService,
    ProductService,
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.

    Creates a shared aiohttp ClientSession with a configured TCP connection pool
    on application startup. The session is reused for all outgoing HTTP calls
    to internal services (Product Service, Payment Service, etc.) to avoid creating
    a new connection per request and to improve performance.

    The session is gracefully closed on application shutdown.
    """

    # Shared HTTP client session with connection pool for internal services
    session = aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=10),
        connector=aiohttp.TCPConnector(
            limit=500,  # total max connections (100 per downstream service + 100 buffer)
            limit_per_host=100,  # max connections per service
            ttl_dns_cache=300,  # DNS cache TTL (seconds)
        ),
    )

    app.state.auth_service = AuthService(session)
    app.state.order_service = OrderService(session)
    app.state.payment_service = PaymentService(session)
    app.state.product_service = ProductService(session)

    yield

    await session.close()


def create_application() -> FastAPI:
    """
    Create an application.

    Returns:
        The application as `FastAPI`.
    """
    app = FastAPI(debug=settings.debug, lifespan=lifespan)
    app.add_middleware(GZipMiddleware, minimum_size=500, compresslevel=4)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

    # remove standard docs routes
    for path in ['/openapi.json', '/docs', '/redoc']:
        for route in list(app.routes):
            if route.path == path:
                app.routes.remove(route)
                break

    router = APIRouter()
    router.include_router(docs_router)
    router.include_router(health_router)
    router.include_router(services_router)

    app.include_router(router)

    return app


application = create_application()
