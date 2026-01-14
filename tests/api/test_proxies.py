import pytest
from fastapi import status


async def test_payments_callback_proxies_post_request(client, app, fake_service_factory):
    service, proxy_mock = fake_service_factory()
    app.state.payment_service = service

    response = await client.post('/payments/callback/wayforpay')

    assert response.status_code == status.HTTP_200_OK

    proxy_mock.assert_awaited_once()
    _, kwargs = proxy_mock.call_args

    assert kwargs['path'] == 'callback/wayforpay'
    assert kwargs['auth_required'] is False


async def test_payments_callback_proxies_get_request_with_params(client, app, fake_service_factory):
    service, proxy_mock = fake_service_factory()
    app.state.payment_service = service

    params = {'param_1': 'value_1', 'param_2': 'value_2'}
    response = await client.get('/payments/callback/wayforpay', params=params)

    assert response.status_code == status.HTTP_200_OK

    proxy_mock.assert_awaited_once()
    _, kwargs = proxy_mock.call_args

    assert kwargs['path'] == 'callback/wayforpay'
    assert kwargs['auth_required'] is False

    for key, value in params.items():
        assert kwargs['request'].query_params[key] == value


@pytest.mark.parametrize(
    'url, expected_proxy_url, service_name',
    [
        ('/auth/api/v1/sign-up', 'api/v1/sign-up', 'auth_service'),
        ('/orders/api/v1/orders', 'api/v1/orders', 'order_service'),
        ('/products/api/v1/catalog', 'api/v1/catalog', 'product_service'),
    ],
)
@pytest.mark.parametrize(
    'method',
    ['POST', 'GET', 'PATCH', 'PUT', 'DELETE', 'OPTION'],
)
async def test_service_url_proxies_request(
    url,
    expected_proxy_url,
    service_name,
    method,
    client,
    app,
    fake_service_factory,
):
    service, proxy_mock = fake_service_factory()
    setattr(app.state, service_name, service)

    response = await client.request(method, url)

    assert response.status_code == status.HTTP_200_OK

    proxy_mock.assert_awaited_once()
    _, kwargs = proxy_mock.call_args

    assert kwargs['path'] == expected_proxy_url


async def test_service_url_proxies_request_when_service_unknown(client, app):
    response = await client.post('/auth-auth/api/v1/sign-up')

    assert response.status_code == status.HTTP_404_NOT_FOUND
