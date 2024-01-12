import json

import pytest


@pytest.fixture
def apigw_event(base_dir) -> dict:
    with open(base_dir / 'sam/events/unit-test-api-user.json', 'r') as f:
        return json.load(f)


def test_user_handler(mock_env, redis_mock, mock_auth, apigw_event: dict, ):
    from func_api_user.app import lambda_handler
    redis_mock._storage = {
        '48a5ac6e-694b-4c3c-831d-ce5bb13f240e':
            {
                "name": 'test',
                'email': 'test',
                'given_name': 'test',
                'family_name': 'test',
                "preferred_username": 'test',
                "zoneinfo": 'test',
                "email_verified": 'test',
            }
    }
    result = lambda_handler(apigw_event, None)

    assert result['statusCode'] == 200
    assert result[
               'body'] == '{"name": "test", "email": "test", "given_name": "test", "family_name": "test", "preferred_username": "test", "zoneinfo": "test", "email_verified": "test"}'
