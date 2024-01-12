import dataclasses
import json
import typing
import uuid
from copy import copy

from aws_lambda_powertools import Metrics
from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from aws_lambda_powertools.utilities.typing import LambdaContext
from chatbot_cloud_util import util
from chatbot_cloud_util.api_request import HumanInputRequest
from chatbot_cloud_util.api_response import HumanInputErrorResponse, HumanInputResponse
from chatbot_cloud_util.aws_api import start_sfn_workflow
from chatbot_cloud_util.base_lambda import (
    BaseApiLambdaHandler,
    BaseWsApiLambdaConfiguration,
)
from chatbot_cloud_util.decorators import (
    handle_exceptions,
    trace_event,
    transform_ws_message,
    ws_login_required,
)
from chatbot_cloud_util.state import HumanInputState, State

from .schema import INPUT_SCHEMA, OUTPUT_SCHEMA

# from aws_xray_sdk.core import patch_all
# patch_all()

metrics = Metrics()

util.adjust_logger()


@dataclasses.dataclass
class LambdaConfiguration(BaseWsApiLambdaConfiguration):
    human_input_workflow_state_machine_arn: str


class LambdaHandler(BaseApiLambdaHandler):
    lambda_configuration_class = LambdaConfiguration
    request_class = HumanInputRequest
    state_class = HumanInputState
    deserialize_request = True
    metric_name_suffix = 'ws-api-human-input'
    protected_handler = True

    def _handle(self, event: typing.Union[APIGatewayProxyEvent, dict], existing_state: State = None):
        self.logger.info('Human input request')
        state = None
        ws_response = None
        try:
            response = HumanInputResponse(
                id=uuid.uuid4(),
                chat_id=self.request.chat_id,
                chat_ts=self.request.chat_ts,
                ts=self.now,
                extra=self.request.extra,
            )
            state = self._build_state(response,
                                      human_input=self.request.human_input,
                                      obfuscate=self.request.obfuscate,
                                      extra=self.request.extra)
            self._start_state_machine_execution(event, response)

            return 200, response, ws_response, state
        except Exception as e:
            self.logger.exception('Unable to handle request')
            response = HumanInputErrorResponse(
                error=str(e),
                chat_id=self.request.chat_id,
                chat_ts=self.request.chat_ts,
                ts=self.now,
                extra=self.request.extra,
            )
            return self._to_status_code(e), response, ws_response, state

    def _start_state_machine_execution(self,
                                       event: typing.Union[APIGatewayProxyEvent, dict],
                                       response: HumanInputResponse):
        state_machine_event = copy(event)  # TODO: clean event based on an input schema of the lambda
        state_machine_event['claims'] = self.claims
        state_machine_event['body'] = response.to_json()
        execution = start_sfn_workflow(
            stateMachineArn=self.configuration.human_input_workflow_state_machine_arn,
            name=str(response.id),
            input=json.dumps(state_machine_event),
        )
        self.logger.info('Started new state machine execution',
                         stateMachine_arn=self.configuration.human_input_workflow_state_machine_arn,
                         execution_arn=execution['executionArn'])


@metrics.log_metrics
@trace_event
@transform_ws_message
# @validator(inbound_schema=INPUT_SCHEMA, outbound_schema=OUTPUT_SCHEMA)
@handle_exceptions
@ws_login_required(event_parent_key='headers')
def lambda_handler(event: dict, context: LambdaContext, claims: dict) -> dict:
    return LambdaHandler(now=util.utcnow()).handle(event, context, claims, metrics)
