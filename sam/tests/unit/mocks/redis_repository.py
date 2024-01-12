import json
from typing import Optional

from chatbot_cloud_util.auth_utils import SessionRepositoryInterface


class RedisRepositoryMock(SessionRepositoryInterface):
    def store_hmac(self, key: str, hmac: dict, expires_in: int = 3600 * 24) -> bool:
        return self.store_session(key, json.dumps(hmac), ex=expires_in)

    def get_hmac(self, hmac_name: str) -> Optional[dict]:
        hmac = self.get_session_data(hmac_name)
        if hmac is None:
            return None
        return json.loads(hmac)

    def __init__(self, *args, **kwargs):
        self._storage = {}

    def get_session_data(self, *args):
        return self._storage.get(args[0])

    def store_session(
            self,
            session_id: str,
            session_data: dict,
            expires_in: int = 3600 * 24,  # seconds
    ):
        return self._storage.update({session_id: session_data})

    def create_session_id(self) -> str:
        return 'test_session_id'

    def store_auth_data(self, session_id: str, auth_data: dict, expires_in: int = 3600) -> bool:  # seconds
        self._storage.update({f'auth:{session_id}': auth_data})
        return True

    def get_auth_data(self, session_id: str):
        return self._storage.get(f'auth:{session_id}')

    def delete_auth_data(self, session_id: str) -> int:
        return self._storage.pop(f'auth:{session_id}', None)

    def cleanup(self):
        self._storage = {}

    def delete_session(self, session_id: str):
        self._storage.pop(session_id, None)
