import asyncio
from typing import (
    AsyncGenerator,
    Generator,
)

import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from gateway_service.main import create_application

pytest_plugins = [
    'tests.fixtures.services',
]


@pytest.fixture
def event_loop() -> Generator:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def app() -> FastAPI:
    _app = create_application()
    return _app


@pytest.fixture
async def client(app) -> AsyncGenerator[AsyncClient]:
    async with AsyncClient(app=app, base_url='http://test') as c:
        yield c
