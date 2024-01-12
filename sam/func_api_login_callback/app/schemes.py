from dataclasses import dataclass
from typing import Optional


@dataclass
class ExchangeResponse:
    token_type: str
    expires_in: int
    access_token: str
    id_token: str
    scope: str
    refresh_token: Optional[str] = None


@dataclass
class UserData:
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
