import json
import typing
from datetime import datetime, timezone
from unittest import mock

import boto3
import pytest
from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from moto import mock_s3, mock_secretsmanager, mock_stepfunctions
from moto.core import DEFAULT_ACCOUNT_ID


@pytest.fixture()
def apigw_event(base_dir) -> typing.Union[APIGatewayProxyEvent, dict]:
    with open(base_dir / 'sam/events/unit-test-ws-api-task-token-event.json') as f:
        return json.load(f)


@pytest.fixture()
def human_input():
    return 'human_input_value'


@pytest.mark.parametrize('expected_status_code,expected_body_keys', [(
        200,
        {'id', 'chat_id', 'chat_ts', 'type'},
)])
def test_lambda_handler(apigw_event: dict, human_input: str,
                        expected_status_code: int, expected_body_keys: typing.Set[str],
                        redis_mock, mock_env, mock_auth: mock.MagicMock, mocker) -> None:
    now = datetime.utcnow().replace(tzinfo=timezone.utc)
    bucket_name = apigw_event['stageVariables']['chatbot_requests_bucket']
    subject = 'anonymous'
    access_token = '6009c7e8-6ba1-4fce-b5bf-82c9959da2f0'
    redis_mock.store_session(
        access_token,
        {'email': subject},
    )
    with mock.patch(
            'chatbot_cloud_util.util.datetime'
    ) as mocked_dt, mock.patch(
        'chatbot_cloud_util.aws_api.resume_sfn_workflow'
    ) as mocked_aws_api, mock_s3(), mock_secretsmanager(), mock_stepfunctions():
        mocked_dt.utcnow = mock.Mock(return_value=now)
        mocked_aws_api.return_value = None

        sm_client = boto3.client('secretsmanager', region_name='us-east-1')
        sm_client.create_secret(Name='jwt-secret-key', SecretString='secret')

        s3_client = boto3.client('s3', region_name='us-east-1')
        s3_client.create_bucket(Bucket=bucket_name)

        sfn_client = boto3.client('stepfunctions', region_name='us-east-1')
        state_machine = sfn_client.create_state_machine(
            name='test-state-machine',
            definition=(
                '"StartAt": "DefaultState",'
                '"States": '
                '{"DefaultState": {"Type": "Fail","Error": "DefaultStateError","Cause": "No Matches!"}}}'
            ),
            roleArn=f'arn:aws:iam::{DEFAULT_ACCOUNT_ID}:role/unknown_sf_role',
            type='STANDARD',
        )
        from func_ws_api_task_token.app import lambda_handler

        test_response = lambda_handler(apigw_event, mock.Mock())
        assert test_response['statusCode'] == expected_status_code
        body = json.loads(test_response['body'])
        assert expected_body_keys.issubset(set(body.keys()))

        # state_machine_executions = sfn_client.list_executions(stateMachineArn=state_machine['stateMachineArn'])
        # assert len(state_machine_executions) == 1

        # state_machine_execution = sfn_client.describe_execution(state_machine_executions[0]['executionArn'])
        # assert {'request_id', 'request_ts', 'status', 'event'}.issubset(
        #     json.loads(state_machine_execution['input']).keys()
        # )
