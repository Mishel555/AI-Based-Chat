import json
from unittest.mock import MagicMock

import boto3
import pytest
from moto import mock_secretsmanager
from requests import Response


@pytest.fixture()
def apigw_event(base_dir) -> dict:
    with open(base_dir / 'sam/events/unit-test-api-logout-event.json') as f:
        return json.load(f)


def test_logout_lambda(redis_mock, mock_env, apigw_event, mocker: MagicMock) -> None:
    from func_api_logout.app import lambda_handler

    access_token = '48a5ac6e-694b-4c3c-831d-ce5bb13f240e'
    jwt_token = 'secret'
    redis_mock.store_session(
        access_token,
        {'access_token': access_token, 'refresh_token': 'qwe'},
    )
    revoke_response = Response()
    revoke_response.status_code = 200
    revoke_token_mock = mocker.patch('func_api_logout.app.revoke_token', return_value=revoke_response)
    validate_access_token_mock = mocker.patch('chatbot_cloud_util.decorators._validate_access_token')
    with mock_secretsmanager():
        sm_client = boto3.client('secretsmanager', region_name='us-east-1')
        sm_client.create_secret(Name='test-jwt-secret-key', SecretString=jwt_token)
        result = lambda_handler(apigw_event, None)

    assert result['statusCode'] == 302
    revoke_token_mock.assert_called()
    validate_access_token_mock.assert_called_once_with(access_token)

    assert result == {
        'headers': {
                'Location': '/',
                'Set-Cookie': 'session=; Expires=Thu, 01 Jan 1970 00:00:00 GMT',
            },
        'statusCode': 302,
    }
