import dataclasses
import typing
import uuid

from aws_lambda_powertools import Metrics
from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from aws_lambda_powertools.utilities.typing import LambdaContext
from chatbot_cloud_util import util
from chatbot_cloud_util.api_response import (
    AssertionsCreatorErrorResponse,
    AssertionsCreatorResponse,
)
from chatbot_cloud_util.base_lambda import (
    BaseStepLambdaConfiguration,
    BaseStepLambdaHandler,
)
from chatbot_cloud_util.decorators import trace_event, validated_jwt_token_claims
from chatbot_cloud_util.factory import get_ac
from chatbot_cloud_util.state import (
    StatementBasedAssertionsCreatorState,
    StatementCreatorState,
)
from chatbot_cloud_util.step_request import AssertionsCreatorStepRequest
from chatbot_cloud_util.step_response import AssertionsCreatorStepResponse
from chatbot_validator.exceptions import NoAssertionsGenerated

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
    request_class = AssertionsCreatorStepRequest
    existing_state_class = StatementCreatorState
    state_class = StatementBasedAssertionsCreatorState
    deserialize_request = True
    metric_name_suffix = 'step-assertions-creator'
    protected_handler = True
    fail_on_error = True

    def _handle(self, event: typing.Union[APIGatewayProxyEvent, dict], existing_state: StatementCreatorState = None):
        self.logger.info('Assertions creator request')

        state = None
        ws_response = None
        try:
            ac = get_ac(self.configuration.llm_name, **event['stageVariables'])
            assertions = ac.set_assertions(existing_state.statement).get_assertions()
            assertions_with_ids = [(uuid.uuid4(), assertion) for assertion in assertions]

            if not assertions:
                raise NoAssertionsGenerated('No assertions were generated')

            responses = [AssertionsCreatorStepResponse(
                id=id,
                chat_id=self.request.chat_id,
                chat_ts=self.request.chat_ts,
                ts=self.now,
            ) for id, _ in assertions_with_ids]

            state = [
                self._build_state(response, statement_id=existing_state.id, assertion=assertion)
                for (id, assertion), response in zip(assertions_with_ids, responses)
            ]
            ws_response = AssertionsCreatorResponse(
                ids=tuple(id for id, _ in assertions_with_ids),
                assertions=tuple(assertions for _, assertions in assertions_with_ids),
                statement_id=existing_state.id,
                chat_id=self.request.chat_id,
                chat_ts=self.request.chat_ts,
                ts=self.now,
                extra=existing_state.extra,
            )
            return 200, responses, ws_response, state
        except Exception as e:
            self.logger.exception('Unable to handle request')
            response = AssertionsCreatorErrorResponse(
                statement_id=existing_state.id,
                error=str(e),
                chat_id=self.request.chat_id,
                chat_ts=self.request.chat_ts,
                ts=self.now,
                extra=existing_state.extra,
            )
            ws_response = response
            return self._to_status_code(e), response, ws_response, state

    def _serialize_response(self, event, status_code, response) -> typing.Union[typing.List[dict], dict]:
        return self._serialize_as_list_of_responses(event, status_code, response, merge_with_event=True)


@metrics.log_metrics
# @validator(inbound_schema=INPUT_SCHEMA, outbound_schema=OUTPUT_SCHEMA)
@trace_event
@validated_jwt_token_claims
def lambda_handler(event: dict, context: LambdaContext, claims: dict) -> dict:
    return LambdaHandler(now=util.utcnow()).handle(event, context, claims, metrics)
