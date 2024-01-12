from abc import ABC, abstractmethod
from typing import Optional, TypedDict


class UserSessionData(TypedDict):
    token_type: str
    expires_in: int
    access_token: str
    id_token: str
    scope: str
    sub: str  # user_id
    name: str
    locale: str
    email: str
    preferred_username: str
    given_name: str
    family_name: str
    zoneinfo: str
    updated_at: int
    email_verified: bool
    issue_date: str
    expires_in: int


class AuthData(TypedDict):
    app_state: str
    code_verifier: str


class SessionRepositoryInterface(ABC):
    @abstractmethod
    def create_session_id(self) -> str:
        ...

    @abstractmethod
    def store_session(
        self,
        session_id: str,
        session_data: UserSessionData,
        expires_in: int = 3600 * 24,  # seconds
    ):
        ...

    @abstractmethod
    def get_session_data(self, session_id: str) -> Optional[UserSessionData]:
        ...

    @abstractmethod
    def store_auth_data(
        self, session_id: str, auth_data: AuthData, expires_in: int = 3600  # seconds
    ) -> bool:
        ...

    @abstractmethod
    def get_auth_data(self, session_id: str) -> Optional[AuthData]:
        ...

    @abstractmethod
    def delete_session(self, session_id: str) -> bool:
        ...

    @abstractmethod
    def delete_auth_data(self, session_id: str) -> bool:
        ...

    @abstractmethod
    def store_hmac(self, key: str, hmac: dict, expires_in: int = 3600 * 24) -> bool:
        ...
        
    @abstractmethod
    def get_hmac(self, hmac_name: str) -> Optional[dict]:
        ...
