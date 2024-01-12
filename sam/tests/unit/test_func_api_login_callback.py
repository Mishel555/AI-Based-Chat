import json

import boto3
import pytest
from moto import mock_secretsmanager
from pytest_mock import MockerFixture


@pytest.fixture
def apigw_event(base_dir):
    with open(base_dir / 'sam/events/unit-test-api-login-callback-event.json') as f:
        return json.load(f)


def test_login_callback_lambda(apigw_event: dict, mock_env, redis_mock, mocker: MockerFixture) -> None:
    from chatbot_cloud_util.auth_utils import get_redis_repository
    from func_api_login_callback.app.schemes import ExchangeResponse, UserData

    session_repository = get_redis_repository()
    session_repository.store_auth_data(
        '48a5ac6e-694b-4c3c-831d-ce5bb13f240e',
        {
            'code_verifier': 'laT3wq_6cI-cAVEBRmexR4e_VxyJb5aKAa2pKn8Ae9I',
            'app_state': 'JyeGrKroMfC6Y_ePN_pBmG5Y_BnsXU4NTp69eZpUjW3dgG7-AjUeFl96TQD4Ai0WGAhELeUyuIdMExn7yG05Jg',
        },
    )
    mocker.patch(
        'func_api_login_callback.app.get_tokens',
        return_value=ExchangeResponse(
            token_type='test',
            expires_in=1,
            access_token='test_access_token',
            id_token='test_id_token',
            scope='test_scope',
        ),
    )
    mocker.patch(
        'func_api_login_callback.app.get_user_info',
        return_value=UserData(
            sub='test_sub',
            name='test_name',
            locale='test_locale',
            email='test_email',
            preferred_username='test_preferred_username',
            given_name='test_given_name',
            family_name='test_family_name',
            zoneinfo='test_zoneinfo',
            updated_at=1,
            email_verified=True,
        ),
    )

    from func_api_login_callback.app import lambda_handler

    with mock_secretsmanager():
        sm_client = boto3.client('secretsmanager', region_name='us-east-1')
        sm_client.create_secret(Name='test-jwt-secret-key', SecretString='secret')
        result = lambda_handler(apigw_event, None)

        assert result['statusCode'] == 302
        assert result == {
            'headers': {
                'Location': 'https://test.host.test/',
                'Set-Cookie': 'session=dGVzdF9hY2Nlc3NfdG9rZW4=; Path=/',
            },
            'statusCode': 302,
        }

    assert session_repository.get_auth_data('48a5ac6e-694b-4c3c-831d-ce5bb13f240e') is None


def test_login_callback_no_session(
    apigw_event: dict,
    mock_env,
    redis_mock,
) -> None:
    from func_api_login_callback.app import lambda_handler

    result = lambda_handler(apigw_event, None)
    assert result == {'body': '{"error": "Session not found"}', 'statusCode': 403}
