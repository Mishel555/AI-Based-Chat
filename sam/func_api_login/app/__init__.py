from chatbot_cloud_util.auth_utils import encode_session, get_redis_repository
from chatbot_cloud_util.auth_utils.envs import REDIRECT_EXTRA_PATH
from chatbot_cloud_util.decorators import handle_exceptions, trace_event
from chatbot_cloud_util.util import get_base_url

from .utils import (
    encode_code_verifier,
    get_redirect_uri,
    make_app_state,
    make_code_verifier,
)

session_repository = get_redis_repository()


@trace_event
@handle_exceptions
def lambda_handler(event: dict, context):
    app_state = make_app_state()
    code_verifier = make_code_verifier()
    code_challenge = encode_code_verifier(code_verifier)

    session_id = session_repository.create_session_id()

    session_repository.store_auth_data(
        session_id,
        {
            "app_state": app_state,
            "code_verifier": code_verifier,
        },
    )

    base_url = get_base_url(event, REDIRECT_EXTRA_PATH)
    return {
        "statusCode": 302,
        "headers": {
            "Location": get_redirect_uri(base_url, app_state, code_challenge),
            "Set-Cookie": f"session={encode_session(session_id)}; Max-Age=1800; Path=/",
        },
    }
