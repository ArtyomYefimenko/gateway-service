import logging

from fastapi import (
    APIRouter,
    Request,
    Response,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=['Services API'])


@router.api_route('/payments/callback/{rest_of_path:path}', methods=['POST', 'GET'])
async def payments_callback(request: Request, rest_of_path: str):
    # payment providers do not know about our jwt token
    service = request.app.state.payment_service
    proxied_path = f'callback/{rest_of_path}'

    logger.info('Proxying payment callback to %s', proxied_path)

    response = await service.proxy(
        request=request,
        path=proxied_path,
        auth_required=False,
    )
    return response


@router.api_route(
    '/{service_name}/api/{rest_of_path:path}',
    methods=['POST', 'GET', 'PATCH', 'PUT', 'DELETE', 'OPTION'],
)
async def proxy_generic(
    request: Request,
    service_name: str,
    rest_of_path: str,
):
    service_map = {
        'auth': request.app.state.auth_service,
        'products': request.app.state.product_service,
        'orders': request.app.state.order_service,
    }

    service = service_map.get(service_name)
    if not service:
        return Response(status_code=404)

    api_path = f'api/{rest_of_path}'

    logger.info('Proxying %s to %s', service_name, api_path)

    auth_required = service_name not in (
        'auth',
        'products',
    )
    response = await service.proxy(
        request=request,
        path=api_path,
        auth_required=auth_required,
    )
    return response
