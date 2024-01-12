import json
import typing
import uuid
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

import boto3
import pytest
from chatbot_cloud_util import util
from chatbot_cloud_util.mixins import WebSocketEnabledApiGatewayEvent
from chatbot_cloud_util.state import ObfuscatorState, StatementCreatorState
from moto import mock_s3, mock_secretsmanager


def existing_state_from(**kwargs):
    return StatementCreatorState(
        id=uuid.UUID('691c5615-ce6c-476e-9155-e451e359ce8f'),
        chat_id=uuid.UUID('8ff3e8e7-6d69-4070-b3f9-c25d7efc36c6'),
        user='anonymous',
        chat_ts=util.parse_ts('2023-05-16T21:45:10.460757Z'),
        ts=util.parse_ts('2023-05-16T21:45:10.460757Z'),
        human_input_id=uuid.UUID('691c5615-ce6c-476e-9155-e451e359ce8f'),
        obfuscator_id=uuid.UUID('691c5615-ce6c-476e-9155-e451e359ce8f'),
        extra='extra-value',
        **kwargs,
    )


@pytest.fixture()
def apigw_event(base_dir) -> dict:
    with open(base_dir / 'sam/events/unit-test-step-task-token-notificator-event.json') as f:
        return json.load(f)


@pytest.mark.parametrize('existing_state,expected_status_code,expected_body_keys', [(
        existing_state_from(statement='The Earth revolves around the Sun, takes about 365.25 days for a full orbit, '
                                      'has a slightly tilted axis, and is the third planet from the Sun.'),
        200,
        {'id', 'chat_id', 'chat_ts'},
)])
def test_lambda_handler(apigw_event: dict, existing_state: ObfuscatorState,
                        expected_status_code: int, expected_body_keys: typing.Set[str],
                        mock_env, mocker) -> None:
    now = datetime.utcnow().replace(tzinfo=timezone.utc)
    task_token = apigw_event['task_token']
    bucket_name = apigw_event['body']['stageVariables']['chatbot_requests_bucket']
    history_bucket_name = apigw_event['body']['stageVariables']['chatbot_chat_history_bucket']
    subject = 'anonymous'

    mock_env['llm_name'] = 'chat_openai'
    mock_env['existing_state_type'] = 'statement'

    with (
        mock.patch('chatbot_cloud_util.aws_api.apigw_by_endpoint_url'),
        mock.patch('chatbot_cloud_util.util.datetime') as mocked_dt,
        mock.patch.object(WebSocketEnabledApiGatewayEvent, '_send_ws_message', lambda *a, **kw: None),
        mock_s3(),
        mock_secretsmanager()
    ):
        mocked_dt.utcnow = mock.Mock(return_value=now)

        sm_client = boto3.client('secretsmanager', region_name='us-east-1')
        sm_client.create_secret(Name='openai-secret-key', SecretString='secret')
        sm_client.create_secret(Name='jwt-secret-key', SecretString='secret')

        s3_client = boto3.client('s3', region_name='us-east-1')
        s3_client.create_bucket(Bucket=bucket_name)
        s3_client.create_bucket(Bucket=history_bucket_name)

        s3_client.put_object(
            Bucket=bucket_name,
            Key=str(Path(f'{str(existing_state.id)}.json')),
            Body=existing_state.to_json().encode('utf-8'),
        )

        from func_step_task_token_notificator.app import lambda_handler

        test_response = lambda_handler(apigw_event, mock.Mock())
        assert test_response['statusCode'] == expected_status_code
        body = json.loads(test_response['body'])
        assert expected_body_keys.issubset(set(body.keys()))
        assert body['id'] == str(existing_state.id)
