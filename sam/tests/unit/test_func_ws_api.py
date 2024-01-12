import json
import typing
from datetime import datetime, timezone
from unittest import mock

import boto3
import pytest
from moto import mock_s3, mock_secretsmanager


@pytest.fixture()
def apigw_event(base_dir) -> dict:
    with open(base_dir / 'sam/events/unit-test-ws-api-event.json') as f:
        return json.load(f)


@pytest.mark.parametrize('expected_status_code,expected_body_keys', [(
        200,
        {'ts'},
)])
def test_lambda_handler(
    apigw_event: dict,
    expected_status_code: int,
    expected_body_keys: typing.Set[str],
    redis_mock,
    mock_env,
    mock_auth: mock.MagicMock,
) -> None:
    now = datetime.utcnow().replace(tzinfo=timezone.utc)
    access_token = '6009c7e8-6ba1-4fce-b5bf-82c9959da2f0'
    redis_mock.store_session(
        access_token,
        {'email': 'subject'},
    )
    with mock.patch('chatbot_cloud_util.util.datetime') as mocked_dt, mock_s3(), mock_secretsmanager():
        mocked_dt.utcnow = mock.Mock(return_value=now)

        sm_client = boto3.client('secretsmanager', region_name='us-east-1')
        sm_client.create_secret(Name='jwt-secret-key', SecretString='secret')
        from func_ws_api.app import lambda_handler

        test_response = lambda_handler(apigw_event, mock.Mock())
        assert test_response['statusCode'] == expected_status_code
        body = json.loads(test_response['body'])
        mock_auth.assert_called_once_with(access_token)
        assert expected_body_keys.issubset(set(body.keys()))
