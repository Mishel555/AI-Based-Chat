import json

import pytest
from pytest_mock import MockerFixture


@pytest.fixture()
def apigw_event(base_dir) -> dict:
    with open(base_dir / 'sam/events/unit-test-api-login-event.json') as f:
        return json.load(f)


def test_login_lambda(apigw_event: dict, mock_env, redis_mock, mocker: MockerFixture) -> None:
    from func_api_login.app import lambda_handler

    with mocker.patch('secrets.token_urlsafe', return_value='test_code_verifier'):
        result = lambda_handler(apigw_event, None)
        assert result['statusCode'] == 302
        assert result['headers'] == {
            'Location': 'https://test.auth0.com/oauth2/default/v1/authorize?client_id=test_client_id&redire'
            'ct_uri=https://test//test_host/auth/login_callback&scope=offline_access openid email profile'
            '&state=test_code_verifier&code_challenge=Qq1fGD0HhxwbmeMrqaebgn1qhvKeguQPXqLd'
            'pmixaM4&code_challenge_method=S256&response_type=code&response_mode=query',
            'Set-Cookie': 'session=dGVzdF9zZXNzaW9uX2lk; Max-Age=1800; Path=/',
        }
