import json
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

import boto3
import pytest
from moto import mock_s3, mock_secretsmanager
from requests import Response


@pytest.fixture()
def apigw_event(base_dir: Path) -> dict:
    with open(base_dir / 'sam/events/unit-test-api-start-chat-event.json') as f:
        return json.load(f)


@pytest.mark.parametrize('expected_status_code,expected_body_keys', [(
        200,
        {'id', 'ts'},
)])
def test_lambda_handler(apigw_event: dict,
                        expected_status_code, expected_body_keys,
                        redis_mock, mock_env, mocker) -> None:
    bucket_name = apigw_event['stageVariables']['chatbot_requests_bucket']
    subject = 'anonymous'
    now = datetime.utcnow().replace(tzinfo=timezone.utc)

    with (mock.patch('chatbot_cloud_util.util.datetime') as mocked_dt,
          mock_s3(), mock_secretsmanager(),
          ):
        access_token = '6009c7e8-6ba1-4fce-b5bf-82c9959da2f0'
        redis_mock.store_session(
            access_token,
            {'email': subject},
        )
        mocked_dt.utcnow = mock.Mock(return_value=now)

        sm_client = boto3.client('secretsmanager', region_name='us-east-1')
        sm_client.create_secret(Name='jwt-secret-key', SecretString='secret')

        s3_client = boto3.client('s3', region_name='us-east-1')
        s3_client.create_bucket(Bucket=bucket_name)

        validate_access_token_mock = mocker.patch('chatbot_cloud_util.decorators._validate_access_token')
        from func_api_start_chat.app import StartChatState, lambda_handler

        test_response = lambda_handler(apigw_event, mock.Mock())
        assert test_response['statusCode'] == expected_status_code
        
        body = json.loads(test_response['body'])
        assert expected_body_keys.issubset(set(body.keys()))
        validate_access_token_mock.assert_called_once_with(access_token)
        
        if test_response['statusCode'] == 200:
            conn = boto3.resource('s3', region_name='us-east-1')
            payload = conn.Object(bucket_name, str(Path(f'{body["id"]}.json'))).get()['Body'].read().decode('utf-8')
            saved_state = StartChatState(**json.loads(payload))

            state = StartChatState(
                id=saved_state.id,
                chat_id=saved_state.id,
                user=subject,
                chat_ts=now,
                ts=now,
                extra=None,
            )
            assert saved_state == state
