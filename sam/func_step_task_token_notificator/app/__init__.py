import dataclasses
import typing

from aws_lambda_powertools import Metrics
from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from aws_lambda_powertools.utilities.typing import LambdaContext
from chatbot_cloud_util import util
from chatbot_cloud_util.api_response import TaskTokenErrorResponse, TaskTokenResponse
from chatbot_cloud_util.base_lambda import (
    BaseStepLambdaConfiguration,
    BaseStepLambdaHandler,
)
from chatbot_cloud_util.decorators import (
    trace_event,
    transform_wait_task_message,
    validated_jwt_token_claims,
)
from chatbot_cloud_util.state import (
    ChatState,
    StatementBasedAssertionsCreatorState,
    StatementCreatorState,
)
from chatbot_cloud_util.step_request import TaskTokenNotificatorStepRequest
from chatbot_cloud_util.step_response import TaskTokenNotificatorStepResponse

from .schema import INPUT_SCHEMA, OUTPUT_SCHEMA

# from aws_xray_sdk.core import patch_all
# patch_all()

metrics = Metrics()

util.adjust_logger()


@dataclasses.dataclass
class LambdaConfiguration(BaseStepLambdaConfiguration):
    existing_state_type: str
    task_token: str


class LambdaHandler(BaseStepLambdaHandler):
    lambda_configuration_class = LambdaConfiguration
    lambda_configuration_event_fields = ('stageVariables', 'requestContext')
    request_class = TaskTokenNotificatorStepRequest
    existing_state_class = ChatState
    deserialize_request = True
    metric_name_suffix = 'step-task-token-notificator'
    protected_handler = True

    def _deserialize_existing_state(self, **kwargs) -> ChatState:
        if self.configuration.existing_state_type == 'assertion':
            return StatementBasedAssertionsCreatorState(**kwargs)
        elif self.configuration.existing_state_type == 'statement':
            return StatementCreatorState(**kwargs)
        raise ValueError(f'Unable to deserialize existing state payload: '
                         f'unsupported existing state type specified: {self.configuration.existing_state_type}')

    def _handle(self, event: typing.Union[APIGatewayProxyEvent, dict], existing_state: ChatState = None):
        self.logger.info('Task token notificator')
        state = None
        ws_response = None
        try:
            response = TaskTokenNotificatorStepResponse(
                id=self.request.id,
                chat_id=self.request.chat_id,
                chat_ts=self.request.chat_ts,
                ts=self.now,
            )
            ws_response = TaskTokenResponse(
                id=self.request.id,
                chat_id=self.request.chat_id,
                chat_ts=self.request.chat_ts,
                ts=self.now,
                task_token=self.configuration.task_token,
                step_type=self.configuration.existing_state_type,
                extra=existing_state.extra,
            )
            return 200, response, ws_response, state
        except Exception as e:
            self.logger.exception('Unable to handle request')
            response = TaskTokenErrorResponse(
                error=str(e),
                id=self.request.id,
                chat_id=self.request.chat_id,
                chat_ts=self.request.chat_ts,
                ts=self.now,
                step_type=self.configuration.existing_state_type,
                extra=existing_state.extra,
            )
            return self._to_status_code(e), response, ws_response, state


@metrics.log_metrics
# @validator(inbound_schema=INPUT_SCHEMA, outbound_schema=OUTPUT_SCHEMA)
@trace_event
@transform_wait_task_message
@validated_jwt_token_claims
def lambda_handler(event: dict, context: LambdaContext, claims: dict) -> dict:
    return LambdaHandler(now=util.utcnow()).handle(event, context, claims, metrics)
