import json
import logging
import os

from fastapi import (
    APIRouter,
    Request,
    Response,
    status,
)
from fastapi.templating import Jinja2Templates

logger = logging.getLogger(__name__)

current_dir = os.path.dirname(os.path.abspath(__file__))
router = APIRouter(tags=['Docs'])
templates = Jinja2Templates(directory=os.path.join(current_dir, '..', 'templates'))


def services_map(request: Request) -> dict:
    return {
        'products': request.app.state.product_service,
        'orders': request.app.state.order_service,
        'payments': request.app.state.payment_service,
        'auth': request.app.state.auth_service,
    }


@router.get('/docs', include_in_schema=False)
async def swagger_ui_proxy(request: Request):
    service_definitions = [
        {'url': '/auth/openapi.json', 'name': 'Auth Service'},
        {'url': '/products/openapi.json', 'name': 'Product Service'},
        {'url': '/orders/openapi.json', 'name': 'Order Service'},
        {'url': '/payments/openapi.json', 'name': 'Payment Service'},
    ]

    return templates.TemplateResponse(
        'swagger.html',
        {
            'request': request,
            'title': 'Gateway API Docs',
            'urls': service_definitions,
            'primary_name': service_definitions[0]['name'],
        },
    )


@router.api_route('/openapi.json', methods=['GET', 'HEAD'])
async def openapi(request: Request):
    referer = request.headers.get('referer', '')
    docs_map = {f'{name}/docs': service for name, service in services_map(request=request)}
    for key, service in docs_map.items():
        if referer.endswith(key):
            return await service.proxy(
                request=request,
                path='openapi.json',
                auth_required=False,
            )

    return Response(status_code=status.HTTP_404_NOT_FOUND)


@router.api_route('/{service_name}/docs', methods=['GET', 'HEAD'])
async def service_docs(request: Request, service_name: str):
    service_map = services_map(request=request)
    service = service_map.get(service_name)
    if not service:
        return Response(status_code=status.HTTP_404_NOT_FOUND)

    return await service.proxy(
        request=request,
        path='docs',
        auth_required=False,
    )


@router.get('/{service_name}/openapi.json', include_in_schema=False)
async def get_service_openapi(request: Request, service_name: str):
    service_map = services_map(request=request)
    service = service_map.get(service_name)
    if not service:
        return Response(status_code=status.HTTP_404_NOT_FOUND)

    response = await service.proxy(
        request=request,
        path='openapi.json',
        auth_required=False,
    )
    if response.status_code != status.HTTP_200_OK:
        return response

    openapi_data = json.loads(response.body)
    openapi_data['servers'] = [{'url': f'/{service_name}', 'description': 'Access via API Gateway'}]
    return Response(content=json.dumps(openapi_data), media_type='application/json')
