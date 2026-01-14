from unittest.mock import AsyncMock

import pytest
from fastapi import (
    Response,
    status,
)


class FakeService:
    def __init__(self, proxy):
        self.proxy = proxy


@pytest.fixture
def fake_service_factory():
    def factory(
        *,
        status_code: int = status.HTTP_200_OK,
        body: bytes | str = b'',
    ) -> tuple[FakeService, AsyncMock]:
        if isinstance(body, str):
            body_bytes = body.encode()
        else:
            body_bytes = body

        proxy_mock = AsyncMock(
            return_value=Response(
                status_code=status_code,
                content=body_bytes,
            )
        )
        return FakeService(proxy_mock), proxy_mock

    return factory
