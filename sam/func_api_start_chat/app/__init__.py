import dataclasses
import typing
import uuid

from aws_lambda_powertools import Metrics
from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from aws_lambda_powertools.utilities.typing import LambdaContext
from chatbot_cloud_util import util
from chatbot_cloud_util.api_request import StartChatRequest
from chatbot_cloud_util.api_response import StartChatResponse
from chatbot_cloud_util.base_lambda import (
    BaseApiLambdaConfiguration,
    BaseApiLambdaHandler,
)
from chatbot_cloud_util.decorators import handle_exceptions, login_required, trace_event
from chatbot_cloud_util.response import ErrorResponse
from chatbot_cloud_util.state import StartChatState, State

# from aws_xray_sdk.core import patch_all
# patch_all()

metrics = Metrics()

util.adjust_logger()


@dataclasses.dataclass
class LambdaConfiguration(BaseApiLambdaConfiguration):
    jwt_secret_key_name: str = None


class LambdaHandler(BaseApiLambdaHandler):
    lambda_configuration_class = LambdaConfiguration
    request_class = StartChatRequest
    state_class = StartChatState
    deserialize_request = True
    metric_name_suffix = 'api-start-chat'
    protected_handler = True
    

    def _handle(self, event: typing.Union[APIGatewayProxyEvent, dict], existing_state: State = None):
        chat_id = uuid.uuid4()
        self.logger = self.logger.bind(chat_id=chat_id)
        self.logger.info('New chat request')
        state = None
        ws_response = None
        try:
            response = StartChatResponse(id=chat_id, ts=self.now)
            state = self._build_state(response)

            return 200, response, ws_response, state
        except Exception as e:
            self.logger.exception('Unable to handle request')
            response = ErrorResponse(
                error=str(e),
                ts=self.now,
            )
            return self._to_status_code(e), response, ws_response, state


@metrics.log_metrics
# @validator(inbound_schema=INPUT_SCHEMA, outbound_schema=OUTPUT_SCHEMA)
@trace_event
@handle_exceptions
@login_required
def lambda_handler(event: dict, context: LambdaContext, claims: dict) -> dict:
    return LambdaHandler(now=util.utcnow()).handle(event, context, claims, metrics)
