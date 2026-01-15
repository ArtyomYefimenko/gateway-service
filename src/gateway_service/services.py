import logging

import aiohttp
import jwt
from fastapi import (
    APIRouter,
    HTTPException,
    Request,
    Response,
    status,
)
from fastapi.security import HTTPBearer

from gateway_service.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer(auto_error=False)


class BaseGatewayService:
    """
    Base class for gateway services.
    One aiohttp.ClientSession per service (connection pooling).
    """

    base_url: str

    def __init__(self, session: aiohttp.ClientSession):
        self.session = session

    async def _build_auth_headers(self, auth_token: str) -> dict:
        """
        Validate JWT and convert payload to headers.
        """

        try:
            payload = jwt.decode(
                auth_token,
                settings.jwt_secret,
                algorithms=['HS256'],
                options={
                    'require': ['exp', 'iat', 'sub', 'jti', 'iss'],
                    'verify_exp': True,
                },
            )
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='JWT expired')
        except jwt.PyJWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid JWT token')

        return {
            'X-User-Id': str(payload['sub']),
        }

    async def proxy(
        self,
        request: Request,
        path: str,
        *,
        auth_required: bool = True,
    ) -> Response:
        """
        Proxy incoming request to downstream service.
        """

        headers = dict(request.headers)
        headers.pop('host', None)
        headers.pop('X-User-Id', None)

        credentials = await security(request)
        auth_token = credentials.credentials if credentials else None

        if auth_required:
            if not auth_token:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='JWT token required')

            headers.update(await self._build_auth_headers(auth_token))

        try:
            async with self.session.request(
                method=request.method,
                url=f'{self.base_url}/{path}',
                params=request.query_params.multi_items(),
                data=await request.body(),
                headers=headers,
            ) as response:
                body = await response.read()

        except (aiohttp.ClientError, aiohttp.ClientTimeout):
            logger.exception('Gateway request failed')
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail='Bad Gateway')

        return Response(
            content=body,
            status_code=response.status,
            headers=dict(response.headers),
        )


class AuthService(BaseGatewayService):
    base_url = settings.auth_service_url


class OrderService(BaseGatewayService):
    base_url = settings.order_service_url


class ProductService(BaseGatewayService):
    base_url = settings.product_service_url


class PaymentService(BaseGatewayService):
    base_url = settings.payment_service_url
