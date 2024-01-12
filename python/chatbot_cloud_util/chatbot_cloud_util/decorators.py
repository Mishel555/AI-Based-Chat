import datetime
import json
import logging
import os
from typing import Callable

from aws_lambda_powertools.middleware_factory import lambda_handler_decorator
from chatbot_cloud_util.auth_utils import (
    encode_session,
    get_client_secret,
    get_session,
    get_session_from_query_params,
    request_access_token,
)
from chatbot_cloud_util.auth_utils.envs import AUTH0_URL, SESSION_RECORD_LIFETIME
from chatbot_cloud_util.auth_utils.exceptions import AuthError, UnauthorizedError
from chatbot_cloud_util.auth_utils.jwt_verifier import get_verifier
from chatbot_cloud_util.auth_utils.session_repository import get_redis_repository
from chatbot_cloud_util.common_exceptions import LambdaHandlerError
from chatbot_cloud_util.util import utcnow
from jose import ExpiredSignatureError

logger = logging.getLogger(__name__)

SESSION_KEY = 'session'
CLAIMS_KEY = 'claims'
TASK_TOKEN_KEY = 'task_token'
ACCESS_KEY_AUDIENCE = os.environ.get('ACCESS_KEY_AUDIENCE', 'api://default')


class ParametersNotFoundError(LambdaHandlerError):
    status_code = 400


@lambda_handler_decorator
def trace_event(handler, event, context):
    if os.environ.get('LOG_APIGW_EVENT'):
        print(json.dumps(event))
        print(context)

    return handler(event, context)


def _validate_access_token(access_token: str):
    verifier = get_verifier(
        'okta',
        {
            'auth0_url': AUTH0_URL,
            'audience': ACCESS_KEY_AUDIENCE,
        }
    )
    verifier.verify_access_token(access_token)


def validate_access_token(event, jwt_token) -> tuple[dict, bool]:
    session_repository = get_redis_repository()
    data = session_repository.get_session_data(jwt_token)

    if data is None:
        raise UnauthorizedError('Do login first')

    new_token = False
    try:
        _validate_access_token(jwt_token)
    except ExpiredSignatureError:
        client_secret = get_client_secret(event)
        refresh_token = data['refresh_token']
        access_token = request_access_token(AUTH0_URL, refresh_token, client_secret)
        data['access_token'] = access_token

        if (session_issue_date := data.get('issue_date')) is None:
            session_issue_date = utcnow() - datetime.timedelta(seconds=SESSION_RECORD_LIFETIME)
            data['issue_date'] = session_issue_date
            session_record_lifetime = SESSION_RECORD_LIFETIME
        else:
            session_issue_date = datetime.datetime.fromisoformat(session_issue_date)
            session_record_lifetime = (utcnow() - session_issue_date).seconds
        session_repository.delete_session(jwt_token)
        session_repository.store_session(
            access_token,
            data,
            session_record_lifetime  # one refresh token is valid for 1 week
        )
        new_token = True
    return data, new_token


@lambda_handler_decorator
def handle_exceptions(handler: Callable[..., dict], event, context):
    try:
        response = handler(event, context)
    except Exception as e:
        logger.exception('Received error')
        if isinstance(e, LambdaHandlerError):
            response = {
                "statusCode": e.status_code,
                "body": json.dumps({'error': str(e)})
            }
            if e.add_extra:
                response['body'].update({
                    'extra': json.dumps(event)
                })
        else:
            logger.exception('Received unhandled error')
            response = {
                "statusCode": 500,
                "body": json.dumps({'error': str(e)})
            }
    return response


@lambda_handler_decorator
def login_required(handler, event, context, algorithms=('RS256',),
                   parent_key: str = 'headers', event_parent_key: str = None):
    container = event[parent_key]
    try:
        jwt_token = get_session(container)
    except AuthError:
        raise
    except Exception as e:
        raise UnauthorizedError('Wrong session format') from e

    data, new_token = validate_access_token(event, jwt_token)

    result = handler(event, context, data)
    if new_token:
        access_token = data['access_token']
        result['headers'][
            'Set-Cookie'] = f'session={encode_session(access_token)}; Path=/; HttpOnly; SameSite=None; Secure'
    return result


@lambda_handler_decorator
def ws_login_required(handler, event, context, algorithms=('RS256',), event_parent_key: str = 'queryStringParameters'):
    container = event.get(event_parent_key)
    if container is None:
        raise ParametersNotFoundError('Query parameters not found. Specify session first')
    try:
        jwt_token = get_session_from_query_params(container)
    except AuthError:
        raise
    except Exception as e:
        raise UnauthorizedError('Wrong session format') from e

    data, new_token = validate_access_token(event, jwt_token)

    result = handler(event, context, data)
    if new_token:
        access_token = data['access_token']
        result['headers'][
            'Set-Cookie'] = f'session={encode_session(access_token)}; Path=/; HttpOnly; SameSite=None; Secure'
    return result


@lambda_handler_decorator
def validated_jwt_token_claims(handler, event, context, event_parent_key: str = None):
    container = event[event_parent_key] if event_parent_key else event
    assert CLAIMS_KEY in container, 'Claims are missing'
    return handler(event, context, container[CLAIMS_KEY])


@lambda_handler_decorator
def transform_ws_message(handler, event, context):
    assert 'body' in event, 'Body is missing'

    transformed = dict(event)
    body = json.loads(transformed.pop('body'))
    assert SESSION_KEY in body, 'Session is missing'
    assert 'body' in body, 'Body is missing...'

    transformed.setdefault('headers', {})
    transformed['headers'].setdefault(SESSION_KEY, body.pop(SESSION_KEY))
    transformed['body'] = body.pop('body')

    return handler(transformed, context)


@lambda_handler_decorator
def transform_wait_task_message(handler, event, context):
    assert 'body' in event, 'Body is missing'
    assert TASK_TOKEN_KEY in event, 'Body is missing'

    transformed = dict(event)
    transformed = transformed.pop('body')
    assert CLAIMS_KEY in transformed, 'Claims are missing'

    transformed.setdefault('requestContext', {}).setdefault(TASK_TOKEN_KEY, event[TASK_TOKEN_KEY])

    return handler(transformed, context)


@lambda_handler_decorator
def jsonify_body(handler: Callable[..., dict], *args, **kwargs):
    response = handler(*args, **kwargs)
    if isinstance(response, dict) and 'body' in response and not isinstance(response['body'], str):
        response['body'] = json.dumps(response['body'])
    return response
