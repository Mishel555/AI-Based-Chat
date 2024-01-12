import logging
from typing import Tuple

import requests
from chatbot_cloud_util.auth_utils.envs import (
    AUTH0_CALLBACK_PATH,
    AUTH0_CLIENT_ID,
    AUTH0_TOKEN_URL_PATH,
    AUTH0_URL,
    AUTH0_USER_DATA_URL_PATH,
)
from chatbot_cloud_util.factory import jwt_key
from yarl import URL

from .exceptions import (
    NoEnoughParametersError,
    NoStageVariableFound,
    TokenNotFoundError,
)
from .schemes import ExchangeResponse, UserData

logger = logging.getLogger(__name__)
EventT = dict


def get_client_secret(event: EventT) -> str:
    if "jwt_secret_key_name" not in event["stageVariables"]:
        raise NoStageVariableFound("wrong configuration for stageVariables")
    return jwt_key(event["stageVariables"]["jwt_secret_key_name"])


def get_tokens(
        redirect_base_url: URL, code: str, code_verifier: str, client_secret: str
) -> ExchangeResponse:
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    redirect_url = redirect_base_url.with_path(
        redirect_base_url.path + AUTH0_CALLBACK_PATH
    ).human_repr()
    query_params = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_url,
        "code_verifier": code_verifier,
    }
    exchange = requests.post(
        AUTH0_URL.with_path(AUTH0_TOKEN_URL_PATH),
        headers=headers,
        data=query_params,
        auth=(
            AUTH0_CLIENT_ID,
            client_secret,
        ),
    ).json()

    if not exchange.get("token_type"):
        raise TokenNotFoundError(f"Auth0 returned body: {exchange}")

    return ExchangeResponse(**exchange)


def get_user_info(access_token: str) -> UserData:
    userinfo_response = requests.get(
        AUTH0_URL.with_path(AUTH0_USER_DATA_URL_PATH),
        headers={"Authorization": f"Bearer {access_token}"},
    ).json()

    return UserData(**userinfo_response)


def get_auth_parameters(event: EventT) -> Tuple[str, str]:
    params = event.get("queryStringParameters", {})
    code, state = params.get("code"), params.get("state")
    if code is None or state is None:
        raise NoEnoughParametersError('"code" or "state" parameters not found')
    return code, state
