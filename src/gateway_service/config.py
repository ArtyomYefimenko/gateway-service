"""
Provide implementation of settings.
"""

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):
    debug: bool = False
    jwt_secret: str = 'jwt_secret'
    jwt_expire_time: int = 3600 * 24 * 7
    auth_service_url: str = 'http://auth-service:8000'
    product_service_url: str = 'http://product-service:8000'
    order_service_url: str = 'http://order-service:8000'
    payment_service_url: str = 'http://payment-service:8000'

    model_config = SettingsConfigDict(
        frozen=True,
        env_file='.env',
        extra='ignore',
    )


settings = Settings()
