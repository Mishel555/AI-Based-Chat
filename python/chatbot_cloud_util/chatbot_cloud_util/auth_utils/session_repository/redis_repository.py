import json
import uuid
from datetime import timedelta
from typing import Optional

from redis import Redis

from .interface import AuthData, SessionRepositoryInterface, UserSessionData


class RedisSessionRepository(SessionRepositoryInterface):
    SESSION_KEY_FORMAT = "session:{}"
    AUTH_DATA_KEY_FORMAT = "auth_data:{}"

    def __init__(self, host: str, port: int):
        self._redis = Redis(host, port)

    def create_session_id(self) -> str:
        return uuid.uuid4().__str__()

    def store_session(
        self,
        session_id: str,
        session_data: UserSessionData,
        expires_in: int = 3600 * 24,  # seconds
    ):
        return self._redis.setex(
            self.SESSION_KEY_FORMAT.format(session_id),
            timedelta(seconds=expires_in),
            json.dumps(session_data),
        )

    def store_auth_data(
        self, session_id: str, auth_data: AuthData, expires_in: int = 3600  # seconds
    ) -> bool:
        return self._redis.setex(
            self.AUTH_DATA_KEY_FORMAT.format(session_id),
            timedelta(seconds=expires_in),
            json.dumps(auth_data),
        )

    def get_auth_data(self, session_id: str) -> Optional[AuthData]:
        auth_data = self._redis.get(self.AUTH_DATA_KEY_FORMAT.format(session_id))
        if auth_data is None:
            return auth_data
        return json.loads(auth_data)

    def delete_auth_data(self, session_id: str) -> bool:
        return self._redis.delete(self.AUTH_DATA_KEY_FORMAT.format(session_id))

    def delete_session(self, session_id: str) -> bool:
        return self._redis.delete(self.SESSION_KEY_FORMAT.format(session_id))

    def get_session_data(self, session_id: str) -> Optional[UserSessionData]:
        session_data = self._redis.get(self.SESSION_KEY_FORMAT.format(session_id))
        if session_data is None:
            return None
        return json.loads(session_data)

    def store_hmac(self, key: str, hmac: dict, expires_in: int = 3600 * 24) -> bool:
        return self._redis.set(key, json.dumps(hmac), ex=expires_in)
        
    def get_hmac(self, hmac_name: str) -> Optional[dict]:
        hmac = self._redis.get(hmac_name)
        if hmac is None:
            return None
        return json.loads(hmac)