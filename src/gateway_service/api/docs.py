import logging

from fastapi import (
    APIRouter,
    Request,
    Response,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=['Docs'])


@router.api_route('/openapi.json', methods=['GET', 'HEAD'])
async def openapi(request: Request):
    referer = request.headers.get('referer', '')
    docs_map = {
        'products/docs': request.app.state.product_service,
        'orders/docs': request.app.state.order_service,
        'payments/docs': request.app.state.payment_service,
        'auth/docs': request.app.state.auth_service,
    }

    for key, service in docs_map.items():
        if referer.endswith(key):
            return await service.proxy(
                request=request,
                path='openapi.json',
                auth_required=False,
            )

    return Response(status_code=404)


@router.api_route('/{service_name}/docs', methods=['GET', 'HEAD'])
async def service_docs(request: Request, service_name: str):
    service_map = {
        'products': request.app.state.product_service,
        'orders': request.app.state.order_service,
        'payments': request.app.state.payment_service,
        'auth': request.app.state.auth_service,
    }

    service = service_map.get(service_name)
    if not service:
        return Response(status_code=404)

    return await service.proxy(
        request=request,
        path='docs',
        auth_required=False,
    )
