import requests
from chatbot_cloud_util.auth_utils import AUTH0_CLIENT_ID, AUTH0_URL
from chatbot_cloud_util.auth_utils.envs import AUTH0_REVOCATION_PATH
from chatbot_cloud_util.auth_utils.jwt_verifier import TokenType


def revoke_token(token: str, token_type: TokenType, client_secret: str) -> requests.Response:
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    payload = {
        "token": token,
        "token_type_hint": token_type.value,
    }

    return requests.post(
        AUTH0_URL.with_path(AUTH0_REVOCATION_PATH),
        headers=headers,
        params=payload,
        auth=(
            AUTH0_CLIENT_ID,
            client_secret,
        ),
    )
