import dataclasses
import json
import logging
import typing
import uuid
from types import TracebackType
from typing import Any, Optional, Union
from uuid import UUID

from aws_lambda_powertools import Metrics
from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from aws_lambda_powertools.utilities.typing import LambdaContext
from chatbot_cloud_util import util
from chatbot_cloud_util.api_response import (
    StatementCreatorErrorResponse,
    StatementCreatorResponse,
)
from chatbot_cloud_util.aws_api import apigw_by_endpoint_url
from chatbot_cloud_util.base_lambda import (
    BaseStepLambdaConfiguration,
    BaseStepLambdaHandler,
)
from chatbot_cloud_util.decorators import trace_event, validated_jwt_token_claims
from chatbot_cloud_util.factory import get_sc
from chatbot_cloud_util.llm_s3_message_history import S3ChatMessageHistory
from chatbot_cloud_util.state import ObfuscatorState, StatementCreatorState
from chatbot_cloud_util.step_request import StatementCreatorStepRequest
from chatbot_cloud_util.step_response import StatementCreatorStepResponse
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import LLMResult
from yarl import URL

# from aws_xray_sdk.core import patch_all
# patch_all()

metrics = Metrics()

util.adjust_logger()


@dataclasses.dataclass
class LambdaConfiguration(BaseStepLambdaConfiguration):
    pass


class StatementCreatorStreamingCallback(StreamingStdOutCallbackHandler):
    def __init__(self, connection_id: str, ws_endpoint_url: Union[URL, str], chat_id: UUID, statement_id: UUID,
                 extra: str, logger: Optional[logging.Logger] = None) -> None:
        super().__init__()
        self._ws_endpoint = URL(ws_endpoint_url) if isinstance(ws_endpoint_url, str) else ws_endpoint_url
        self._ws_connection_id = connection_id
        self._chat_id = str(chat_id)
        self._statement_id = str(statement_id)
        self._extra = extra
        self.apigw_management_client = apigw_by_endpoint_url(endpoint_url=self._ws_endpoint.human_repr())
        self.logger = logger or logging.getLogger(__name__)
        self._traceback: Optional[TracebackType] = None

    def _prepare_stream_response(self, token: str) -> str:
        response = {
            'type': 'stream',
            'id': str(self._statement_id),
            'chat_id': self._chat_id,
            'message': token,
            'extra': self._extra,
        }
        return json.dumps(response)

    def on_llm_new_token(self, token: str, *, run_id: UUID, parent_run_id: Optional[UUID] = None, **kwargs: Any) -> Any:
        try:
            self.apigw_management_client.post_to_connection(
                ConnectionId=self._ws_connection_id,
                Data=self._prepare_stream_response(token),
            )
        except Exception as e:
            self.logger.error(f'Unable to send token to websocket. Gor error {e}', exc_info=False)
            self._traceback = e.__traceback__

    def on_llm_error(self, response: LLMResult, **kwargs: Any) -> None:
        if self._traceback is not None:
            self.logger.error(f'During sending stream error occurred: {self._traceback}', exc_info=False)


class LambdaHandler(BaseStepLambdaHandler):
    lambda_configuration_class = LambdaConfiguration
    request_class = StatementCreatorStepRequest
    existing_state_class = ObfuscatorState
    state_class = StatementCreatorState
    deserialize_request = True
    metric_name_suffix = 'step-statement-creator'
    protected_handler = True

    def _create_callback(self, event: typing.Union[APIGatewayProxyEvent, dict],
                         existing_state: ObfuscatorState,
                         statement_id: uuid.UUID):
        domain = event.get('requestContext', {}).get('domainName')
        stage = event.get('requestContext', {}).get('stage')
        connection_id = event.get('requestContext', {}).get('connectionId')
        ws_endpoint_url = URL(f'https://{domain}/{stage}')
        return StatementCreatorStreamingCallback(
            connection_id=connection_id,
            ws_endpoint_url=ws_endpoint_url,
            chat_id=self.request.chat_id,
            statement_id=statement_id,
            extra=existing_state.extra,
            logger=self.logger
        )

    def _handle(self, event: typing.Union[APIGatewayProxyEvent, dict], existing_state: ObfuscatorState = None):
        self.logger.info('Statement creator request')
        state = None
        ws_response = None
        try:
            s3_object_prefix = self.configuration.chatbot_chat_history_prefix_tpl.format(
                year=existing_state.chat_ts.year,
                month=existing_state.chat_ts.month,
                day=existing_state.chat_ts.day,
                chat_id=existing_state.chat_id,
            )
            memory = S3ChatMessageHistory(
                bucket_name=self.configuration.chatbot_chat_history_bucket,
                bucket_object_prefix_tpl=s3_object_prefix,
            )
            memory = ConversationBufferWindowMemory(chat_memory=memory, k=20)
            statement_id = uuid.uuid4()
            sc = get_sc(
                self.configuration.llm_name,
                memory=memory,
                llm_kwargs=dict(
                    streaming=True,
                    callbacks=[self._create_callback(event, existing_state, statement_id)]
                ),
                **event['stageVariables']
            )
            statement = sc.set_statement(existing_state.obfuscated).get_statement()
            response = StatementCreatorStepResponse(
                id=statement_id,
                chat_id=self.request.chat_id,
                chat_ts=self.request.chat_ts,
                ts=self.now,
            )
            state = self._build_state(
                response,
                human_input_id=existing_state.human_input_id,
                obfuscator_id=existing_state.id,
                statement=statement,
                extra=existing_state.extra
            )
            ws_response = StatementCreatorResponse(
                id=response.id,
                human_input_id=existing_state.human_input_id,
                statement=statement,
                chat_id=self.request.chat_id,
                chat_ts=self.request.chat_ts,
                ts=self.now,
                extra=existing_state.extra,
            )
            return 200, response, ws_response, state
        except Exception as e:
            self.logger.exception('Unable to handle request')
            response = StatementCreatorErrorResponse(
                human_input_id=existing_state.human_input_id,
                error=str(e),
                chat_id=self.request.chat_id,
                chat_ts=self.request.chat_ts,
                ts=self.now,
                extra=existing_state.extra,
            )
            ws_response = response
            return self._to_status_code(e), response, ws_response, state


@metrics.log_metrics
# @validator(inbound_schema=INPUT_SCHEMA, outbound_schema=OUTPUT_SCHEMA)
@trace_event
@validated_jwt_token_claims
def lambda_handler(event: dict, context: LambdaContext, claims: dict) -> dict:
    return LambdaHandler(now=util.utcnow()).handle(event, context, claims, metrics)
