import base64
import binascii
import json
import os

import requests
from chatbot_cloud_util.auth_utils.exceptions import (
    CookieDecodeError,
    CookieNotFoundError,
    NoStageVariableFoundError,
    SessionNotFoundError,
)
from chatbot_cloud_util.factory import jwt_key
from jose import jwk
from yarl import URL

from .envs import AUTH0_CLIENT_ID, AUTH0_TOKEN_URL_PATH, AUTH0_URL
from .session_repository import (
    AuthData,
    RedisSessionRepository,
    SessionRepositoryInterface,
    UserSessionData,
    get_redis_repository,
)

EventT = dict


def encode_session(session_id: str) -> str:
    encoded = session_id.encode("utf-8")
    return base64.b64encode(encoded).decode("utf-8")


def decode_session(session_str: str) -> str:
    return base64.b64decode(session_str.encode("utf-8")).decode("utf-8")


def get_auth_key() -> jwk.RSAKey:
    JWKS_KEY = os.environ["JWKS_KEY"]
    keys = base64.b64decode(JWKS_KEY).decode("utf-8")
    for key in json.loads(keys)["keys"]:
        return jwk.construct(key)


def _find_security_cookie(cookie_str: str) -> str:
    cookies = cookie_str.split(";")
    for cookie in filter(lambda x: x.strip().startswith("session="), cookies):
        return cookie.split("=", 1)[1]
    raise CookieNotFoundError("Session cookie not found")


def get_session(container: dict) -> str:
    cookie = container.get("Cookie")
    if cookie is None:
        cookie = container.get("cookie")
    if cookie is None:
        raise CookieNotFoundError("No cookies for request")
    encoded_cookie = _find_security_cookie(cookie)
    try:
        return decode_session(encoded_cookie)
    except binascii.Error:
        raise CookieDecodeError("Wrong security cookie format")


def get_session_from_query_params(container: dict) -> str:
    encoded_cookie = container.get("session")
    if encoded_cookie is None:
        raise SessionNotFoundError("No session specified for request")
    try:
        return decode_session(encoded_cookie)
    except binascii.Error:
        raise CookieDecodeError("Wrong security cookie format")
    
    
def request_access_token(base_url: URL, refresh_token: str, client_secret: str) -> str:
    query_params ={
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
    }
    exchange = requests.post(
        base_url.with_path(AUTH0_TOKEN_URL_PATH),
        data=query_params,
        auth=(
            AUTH0_CLIENT_ID,
            client_secret,
        ),
    ).json()
    return exchange['access_token']
    
    

def get_client_secret(event: EventT) -> str:
    if "jwt_secret_key_name" not in event["stageVariables"]:
        raise NoStageVariableFoundError("wrong configuration for stageVariables")
    return jwt_key(event["stageVariables"]["jwt_secret_key_name"])