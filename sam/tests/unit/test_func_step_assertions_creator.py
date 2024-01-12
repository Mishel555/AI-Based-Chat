import json
import typing
import uuid
from contextlib import nullcontext
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

import boto3
import pytest
from chatbot_cloud_util import util
from chatbot_cloud_util.mixins import WebSocketEnabledApiGatewayEvent
from chatbot_cloud_util.state import (
    StatementBasedAssertionsCreatorState,
    StatementCreatorState,
)
from chatbot_validator.assertions import AssertionChain
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


def assertions() -> typing.List[str]:
    return [
        'The Earth revolves around the Sun.',
        'The Earth takes 365.25 days to fully orbit the sun.',
        'The Earth has a slightly tilted axis.',
        'The Earth is the third planet from the Sun.',
    ]


def empty_assertions() -> typing.List[str]:
    return []


@pytest.fixture()
def apigw_event(base_dir: Path) -> dict:
    with open(base_dir / 'sam/events/unit-test-step-assertions-creator-event.json') as f:
        return json.load(f)


@pytest.mark.parametrize('existing_state,assertions,expected_status_codes,expected_body_keys,expected_to_fail', [(
        existing_state_from(statement='The Earth revolves around the Sun, takes about 365.25 days for a full orbit, '
                                      'has a slightly tilted axis, and is the third planet from the Sun.'),
        assertions(),
        [200, 200, 200, 200],
        {'id', 'chat_id', 'chat_ts'},
        False,
), (
        existing_state_from(statement='The Earth revolves around the Sun, takes about 365.25 days for a full orbit, '
                                      'has a slightly tilted axis, and is the third planet from the Sun.'),
        empty_assertions(),
        [],
        {'id', 'chat_id', 'chat_ts'},
        True,
)])
def test_lambda_handler(apigw_event: dict, existing_state: StatementCreatorState, assertions: typing.List[str],
                        expected_status_codes: typing.List[int], expected_body_keys: typing.Set[str],
                        expected_to_fail: bool,
                        mock_env, mocker) -> None:
    now = datetime.utcnow().replace(tzinfo=timezone.utc)
    bucket_name = apigw_event['stageVariables']['chatbot_requests_bucket']
    subject = 'anonymous'

    mock_env['llm_name'] = 'chat_openai'

    with mock.patch('chatbot_cloud_util.util.datetime') as mocked_dt, mock.patch.object(
            AssertionChain, '__call__', lambda *a, **kw: assertions
    ), mock.patch.object(
        WebSocketEnabledApiGatewayEvent, '_send_ws_message', lambda *a, **kw: None
    ), mock_s3(), mock_secretsmanager():
        mocked_dt.utcnow = mock.Mock(return_value=now)

        sm_client = boto3.client('secretsmanager', region_name='us-east-1')
        sm_client.create_secret(Name='openai-secret-key', SecretString='secret')
        sm_client.create_secret(Name='jwt-secret-key', SecretString='secret')

        s3_client = boto3.client('s3', region_name='us-east-1')
        s3_client.create_bucket(Bucket=bucket_name)

        s3_client.put_object(
            Bucket=bucket_name,
            Key=str(Path(f'{str(existing_state.id)}.json')),
            Body=existing_state.to_json().encode('utf-8'),
        )
        with pytest.raises(AssertionError) if expected_to_fail else nullcontext():
            # TODO: maybe improve negative test scenario
            from func_step_assertions_creator.app import lambda_handler

            test_response = lambda_handler(apigw_event, mock.Mock())
            for response, expected_status_code in zip(test_response, expected_status_codes):
                assert response['statusCode'] == expected_status_code
                assert expected_body_keys.issubset(set(json.loads(response['body']).keys()))
            body = [json.loads(response['body']) for response in test_response]

            conn = boto3.resource('s3', region_name='us-east-1')
            for assertion, b in zip(assertions, body):
                payload = conn.Object(bucket_name, str(Path(f'{b["id"]}.json'))).get()['Body'].read().decode('utf-8')
                saved_state = StatementBasedAssertionsCreatorState(**json.loads(payload))

                state = StatementBasedAssertionsCreatorState(
                    id=saved_state.id,
                    chat_id=existing_state.chat_id,
                    user=subject,
                    chat_ts=existing_state.chat_ts,
                    ts=now,
                    statement_id=existing_state.id,
                    assertion=assertion,
                    extra=None,
                )
                assert saved_state == state
