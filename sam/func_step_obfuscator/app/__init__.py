import dataclasses
import typing
import uuid

from aws_lambda_powertools import Metrics
from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from aws_lambda_powertools.utilities.typing import LambdaContext
from chatbot_cloud_util import util
from chatbot_cloud_util.base_lambda import (
    BaseStepLambdaConfiguration,
    BaseStepLambdaHandler,
)
from chatbot_cloud_util.decorators import trace_event, validated_jwt_token_claims
from chatbot_cloud_util.response import ErrorChatResponse
from chatbot_cloud_util.state import HumanInputState, ObfuscatorState
from chatbot_cloud_util.step_request import ObfuscatorStepRequest
from chatbot_cloud_util.step_response import ObfuscatorStepResponse

from .schema import INPUT_SCHEMA, OUTPUT_SCHEMA

# from aws_xray_sdk.core import patch_all
# patch_all()

metrics = Metrics()

util.adjust_logger()


@dataclasses.dataclass
class LambdaConfiguration(BaseStepLambdaConfiguration):
    pass


class LambdaHandler(BaseStepLambdaHandler):
    lambda_configuration_class = LambdaConfiguration
    request_class = ObfuscatorStepRequest
    existing_state_class = HumanInputState
    state_class = ObfuscatorState
    deserialize_request = True
    metric_name_suffix = 'step-obfuscator'
    protected_handler = True

    def _handle(self, event: typing.Union[APIGatewayProxyEvent, dict], existing_state: HumanInputState = None):
        self.logger.info('Obfuscator request')
        state = None
        ws_response = None
        try:
            obfuscated = existing_state.human_input
            if existing_state.obfuscate:
                # TODO: obfuscate user query
                pass

            response = ObfuscatorStepResponse(
                id=uuid.uuid4(),
                chat_id=self.request.chat_id,
                chat_ts=self.request.chat_ts,
                ts=self.now,
            )
            state = self._build_state(response, human_input_id=existing_state.id, obfuscated=obfuscated,
                                      extra=existing_state.extra)
            return 200, response, ws_response, state
        except Exception as e:
            self.logger.exception('Unable to handle request')
            response = ErrorChatResponse(
                error=str(e),
                chat_id=self.request.chat_id,
                chat_ts=self.request.chat_ts,
                ts=self.now,
            )
            return self._to_status_code(e), response, ws_response, state


@metrics.log_metrics
# @validator(inbound_schema=INPUT_SCHEMA, outbound_schema=OUTPUT_SCHEMA)
@trace_event
@validated_jwt_token_claims
def lambda_handler(event: dict, context: LambdaContext, claims: dict) -> dict:
    return LambdaHandler(now=util.utcnow()).handle(event, context, claims, metrics)
