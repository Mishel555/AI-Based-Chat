import base64
import hashlib
import secrets

from chatbot_cloud_util.auth_utils.envs import (
    AUTH0_APPLICATION_ID,
    AUTH0_CALLBACK_PATH,
    AUTH0_CLIENT_ID,
    AUTH0_URL,
)
from yarl import URL


def make_app_state() -> str:
    return secrets.token_urlsafe(64)


def make_code_verifier() -> str:
    return secrets.token_urlsafe(64)


def encode_code_verifier(code_verifier: str) -> str:
    hashed = hashlib.sha256(code_verifier.encode("ascii")).digest()
    encoded = base64.urlsafe_b64encode(hashed)
    return encoded.decode("ascii").strip("=")


def get_redirect_uri(redirect_base_url: URL, app_state: str, code_challenge: str) -> str:
    redirect_url = redirect_base_url / AUTH0_CALLBACK_PATH
    query_params = {
        "client_id": AUTH0_CLIENT_ID,
        "redirect_uri": redirect_url.human_repr(),
        "scope": "offline_access openid email profile",
        "state": app_state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "response_type": "code",
        "response_mode": "query",
    }

    return AUTH0_URL.with_path(f"/oauth2/{AUTH0_APPLICATION_ID}/v1/authorize").with_query(query_params).human_repr()
