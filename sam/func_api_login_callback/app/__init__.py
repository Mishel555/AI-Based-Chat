from dataclasses import asdict
from typing import Any, Optional

from aws_lambda_powertools import Metrics
from chatbot_cloud_util.auth_utils import (
    AuthData,
    encode_session,
    get_redis_repository,
    get_session,
)
from chatbot_cloud_util.auth_utils.envs import (
    REDIRECT_EXTRA_PATH,
    SESSION_RECORD_LIFETIME,
    SUCCESS_LOGIN_REDIRECT_PATH,
)
from chatbot_cloud_util.auth_utils.exceptions import SessionNotFoundError
from chatbot_cloud_util.decorators import handle_exceptions, jsonify_body, trace_event
from chatbot_cloud_util.util import adjust_logger, get_base_url, utcnow

from .exceptions import AppStateDoesNotMatchError, CodeError
from .utils import (
    EventT,
    get_auth_parameters,
    get_client_secret,
    get_tokens,
    get_user_info,
)

metrics = Metrics()

adjust_logger()

session_repository = get_redis_repository()


@trace_event
@handle_exceptions
@jsonify_body
def lambda_handler(event: EventT, context) -> dict[str, Any]:
    code, app_state = get_auth_parameters(event)
    session_id = get_session(event["headers"])
    auth_data: Optional[AuthData] = session_repository.get_auth_data(session_id)

    if auth_data is None:
        raise SessionNotFoundError("Session not found")

    session_app_state = auth_data["app_state"]
    session_code = auth_data["code_verifier"]
    session_repository.delete_auth_data(session_id)

    if app_state != session_app_state:
        raise AppStateDoesNotMatchError("The app state does not match")

    if not session_code:
        raise CodeError("The code was not returned or is not accessible")

    client_secret = get_client_secret(event)
    base_url = get_base_url(event, REDIRECT_EXTRA_PATH)
    exchange = get_tokens(base_url, code, session_code, client_secret)
    user_info = get_user_info(exchange.access_token)

    session_record_lifetime = SESSION_RECORD_LIFETIME
    session_repository.store_session(
        exchange.access_token,
        {
            **asdict(exchange), **asdict(user_info), "issue_date": utcnow().isoformat(),
            "expires_in": session_record_lifetime
        },
        expires_in=session_record_lifetime,
    )

    return {
        "statusCode": 302,
        "headers": {
            "Location": (base_url / SUCCESS_LOGIN_REDIRECT_PATH).human_repr(),
            "Set-Cookie": f"session={encode_session(exchange.access_token)}; Path=/",
        },
    }
