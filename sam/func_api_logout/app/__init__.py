import chatbot_cloud_util.util as util
import requests
from aws_lambda_powertools import Metrics
from chatbot_cloud_util.auth_utils import (
    UserSessionData,
    get_client_secret,
    get_redis_repository,
    get_session,
)
from chatbot_cloud_util.auth_utils.envs import LOGOUT_REDIRECT_PATH
from chatbot_cloud_util.auth_utils.jwt_verifier import TokenType
from chatbot_cloud_util.decorators import handle_exceptions, login_required, trace_event

from .exceptions import RevokeTokenError
from .utils import revoke_token

metrics = Metrics()

util.adjust_logger()


def _check_revoke_response(revoke_response: requests.Response):
    if revoke_response.status_code != 200:
        err = RevokeTokenError(
            f"Failed to revoke token: {revoke_response.status_code} {revoke_response.text}"
        )
        err.status_code = revoke_response.status_code
        raise err


@trace_event
@handle_exceptions
@login_required
def lambda_handler(event: dict, context, claims: UserSessionData):
    session_id = get_session(event['headers'])
    session_repository = get_redis_repository()
    user_data = session_repository.get_session_data(session_id)

    access_token = user_data["access_token"]
    secret = get_client_secret(event)
    revoke_response = revoke_token(
        access_token,
        TokenType.access_token,
        secret,
    )
    _check_revoke_response(revoke_response)
    if (refresh_token := user_data.get("refresh_token")) is not None:
        revoke_response = revoke_token(refresh_token, TokenType.refresh_token, secret)
        _check_revoke_response(revoke_response)

    session_repository.delete_session(session_id)
    return {
        "statusCode": 302,
        "headers": {
            "Set-Cookie": "session=; Expires=Thu, 01 Jan 1970 00:00:00 GMT",
            "Location": LOGOUT_REDIRECT_PATH,
        },
    }
