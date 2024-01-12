import os
from typing import Optional

from .interface import AuthData, SessionRepositoryInterface, UserSessionData
from .redis_repository import RedisSessionRepository

redis_repository = None


def get_redis_repository(
    host: Optional[str] = None,
    port: Optional[int] = None,
    host_env_name: str = "REDIS_HOST",
    port_env_name: str = "REDIS_PORT",
) -> RedisSessionRepository:
    global redis_repository
    if redis_repository is None:
        if host is None:
            host = os.environ[host_env_name]
        if port is None:
            port = os.environ[port_env_name]
        redis_repository = RedisSessionRepository(host, port)
    return redis_repository
