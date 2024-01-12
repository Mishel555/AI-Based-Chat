import abc
import dataclasses
import json
import os
import typing
from datetime import datetime
from inspect import signature
from pathlib import Path

import chatbot_cloud_util.util as util
from aws_lambda_powertools import Metrics
from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from aws_lambda_powertools.utilities.typing import LambdaContext
from chatbot_cloud_util.aws_api import read_str_from_s3, write_str_to_s3
from chatbot_cloud_util.common_exceptions import LambdaHandlerError
from chatbot_cloud_util.mixins import (
    MeasurableApiGatewayEvent,
    WebSocketEnabledApiGatewayEvent,
)
from chatbot_cloud_util.request import ChatRequest
from chatbot_cloud_util.response import ErrorChatResponse, ErrorResponse, Response
from chatbot_cloud_util.state import State
from chatbot_validator.exceptions import ValidatorError
from loguru import logger


@dataclasses.dataclass
class BaseLambdaConfiguration(abc.ABC):
    chatbot_requests_bucket: str
    chatbot_request_prefix_tpl: str

    chatbot_chat_history_bucket: str
    chatbot_chat_history_prefix_tpl: str

    def __post_init__(self):
        pass

    @classmethod
    def from_event(cls, event: dict, parent_keys=None, use_env_vars=True, **kwargs):
        cls_fields = {field for field in signature(cls).parameters}

        container_values = {
            name: val
            for parent_key in (parent_keys or ['stageVariables'])
            for name, val in event.get(parent_key, {}).items() if name in cls_fields
        }
        env_values = {
            name.lower(): val for name, val in os.environ.items() if name.lower() in cls_fields
        } if use_env_vars else {}

        return cls(**{**container_values, **env_values, **kwargs})


@dataclasses.dataclass
class BaseWsApiLambdaConfiguration(BaseLambdaConfiguration):
    jwt_secret_key_name: str


@dataclasses.dataclass
class BaseApiLambdaConfiguration(BaseLambdaConfiguration):
    allow_headers: typing.Optional[str] = None
    allow_origins: typing.Optional[str] = None
    allow_methods: typing.Optional[str] = None
    allow_credentials: typing.Optional[str] = None


@dataclasses.dataclass
class BaseStepLambdaConfiguration(BaseLambdaConfiguration):
    jwt_secret_key_name: str
    openai_secret_key_name: str
    llm_name: str


class BaseLambdaHandler(abc.ABC, MeasurableApiGatewayEvent, WebSocketEnabledApiGatewayEvent):
    lambda_configuration_class = None
    lambda_configuration_event_fields = None
    request_class = None
    existing_state_class = None
    state_class = None
    deserialize_request = False
    metric_name_suffix = None
    protected_handler = True
    websocket_enabled = False
    fail_on_error = False

    def __init__(self, now: typing.Optional[datetime] = None):
        self.now = now or util.utcnow()
        self.configuration = None
        self.logger = None
        self.request = None
        self.claims = None
        self.subject = None

    def _metric_name(self, name):
        return f'{name}-{self.metric_name_suffix}'

    def _to_configuration(self, event: typing.Union[APIGatewayProxyEvent, dict]):
        return getattr(self.lambda_configuration_class, 'from_event')(
            event, parent_keys=self.lambda_configuration_event_fields, use_env_vars=True)

    def _to_request(self, event: typing.Union[APIGatewayProxyEvent, dict]):
        return getattr(self.request_class, 'from_event')(
            event, deserialize_container=self.deserialize_request)

    def _read_existing_state_from_s3(self) -> State:
        # request_id: uuid.UUID,
        #                                       configuration: BaseLambdaConfiguration,
        #                                       context_object_name: str, ts: datetime
        request = self.request
        bucket_name = self.configuration.chatbot_requests_bucket
        object_key = str(Path(
            self.configuration.chatbot_request_prefix_tpl.format(
                year=request.chat_ts.year, month=request.chat_ts.month, day=request.chat_ts.day,
                chat_id=str(request.chat_id), id=str(request.id)
            ),
        ))
        return self._deserialize_existing_state(**json.loads(read_str_from_s3(bucket_name, object_key)))

    def _write_state_to_s3(self, state: State):
        write_str_to_s3(
            self.configuration.chatbot_requests_bucket,
            str(Path(
                self.configuration.chatbot_request_prefix_tpl.format(
                    year=state.chat_ts.year, month=state.chat_ts.month, day=state.chat_ts.day,
                    chat_id=str(state.chat_id), id=str(state.id)
                ),
            )),
            self._serialize_state(state),
        )

    def _should_have_existing_state(self):
        return self.existing_state_class is not None

    def _deserialize_existing_state(self, **kwargs) -> State:
        return self.existing_state_class(**kwargs)

    def _serialize_state(self, state: State) -> str:
        return state.to_json()

    @abc.abstractmethod
    def _handle(self, event: typing.Union[APIGatewayProxyEvent, dict], existing_state: typing.Optional[State] = None):
        pass

    def _build_state(self, response: Response, **kwargs):
        return getattr(self.state_class, 'build_state')(
            request=self.request, response=response, user=self.subject, **kwargs,
        )

    def handle(self, event: typing.Union[APIGatewayProxyEvent, dict], context: LambdaContext,
               claims: dict, metrics: Metrics):
        self.logger = logger.bind(aws_request_id=context.aws_request_id)

        try:
            self.claims = claims if self.protected_handler else None
            self.subject = claims['email'] if self.protected_handler else None
            self.logger = self.logger.bind(user=self.subject)

            self.configuration = self._to_configuration(event)
            self.request = self._to_request(event)

            if hasattr(self.request, 'id'):
                self.logger.bind(request_id=self.request.id)
            if isinstance(self.request, ChatRequest):
                self.logger.bind(chat_id=self.request.chat_id)
                self.logger.bind(chat_ts=self.request.chat_ts)

            if self._should_have_existing_state():
                with self._measure_time(event, metrics, name=self._metric_name('load-state')):
                    existing_state = self._read_existing_state_from_s3()
                    assert existing_state.user == self.subject, 'Wrong JWT owner'
            else:
                existing_state = None

            with self._measure_time(event, metrics, name=self._metric_name('handle')):
                status_code, response, ws_response, state = self._handle(event, existing_state)

            if self.state_class and state:
                with self._measure_time(event, metrics, name=self._metric_name('save-state')):
                    states = [state] if isinstance(state, State) else state
                    for state in states:
                        self._write_state_to_s3(state)
        except Exception as e:
            self.logger.exception('Request processing failed')
            status_code = self._to_status_code(e)
            ws_response = response = ErrorChatResponse(
                error=str(e),
                chat_id=self.request.chat_id, chat_ts=self.request.chat_ts, ts=self.now,
            ) if isinstance(self.request, ChatRequest) else ErrorResponse(error=str(e), ts=self.now)

        if ws_response:
            self._try_send_ws_response(event, ws_response)

        if self.fail_on_error:
            assert status_code == 200

        return self._serialize_response(event, status_code, response)

    @staticmethod
    def _to_status_code(e: Exception) -> int:
        return e.status_code if isinstance(e, (LambdaHandlerError, ValidatorError)) else 500

    def _try_send_ws_response(self, event, response: Response):
        try:
            if self.websocket_enabled and response:
                self._send_ws_message(event, response.to_json())
            elif self.websocket_enabled:
                self.logger.warning('No websocket response specified')
            elif response:
                self.logger.warning('Not websocket enabled handler, no ws_response expected')
        except Exception:
            logger.exception('Unable to send response to websocket, ignoring...')

    @staticmethod
    def _serialize_as_list_of_responses(event, status_code, response, headers=None,
                                        *args, merge_with_event: bool) -> typing.Union[typing.List[dict], dict]:
        if isinstance(response, Response):
            res = [response.to_json()]
        elif type(response) in (list, tuple):
            res = [r.to_json() for r in response]
        else:
            raise ValueError(f'Unsupported response specified: {type(response)}')

        res = [
            {'statusCode': status_code, 'headers': headers, 'body': r} for r in res
        ] if headers else [{'statusCode': status_code, 'body': r} for r in res]

        return [{**event, **r} for r in res] if merge_with_event else res

    @staticmethod
    def _serialize_as_single_response(event, status_code, response, headers=None,
                                      *args, merge_with_event: bool) -> typing.Union[typing.List[dict], dict]:
        if isinstance(response, Response):
            res = response.to_json()
        elif type(response) in (list, tuple):
            res = json.dumps([r.to_safe_dict() for r in response])
        else:
            raise ValueError(f'Unsupported response specified: {type(response)}')

        res = {'statusCode': status_code, 'body': res}
        if headers:
            res['headers'] = headers

        return {**event, **res} if merge_with_event else res

    @abc.abstractmethod
    def _serialize_response(self, event, status_code, response) -> typing.Union[typing.List[dict], dict]:
        pass


class BaseApiLambdaHandler(BaseLambdaHandler):
    """
    API lambda always accepts API GW event, does the work, and returns only statusCode, headers and body.
    """

    def _serialize_response(self, event, status_code, response) -> typing.Union[typing.List[dict], dict]:
        headers = {}
        if isinstance(self.configuration, BaseApiLambdaConfiguration):
            if self.configuration.allow_headers:
                headers['Access-Control-Allow-Headers'] = self.configuration.allow_headers
            if self.configuration.allow_methods:
                headers['Access-Control-Allow-Methods'] = self.configuration.allow_methods
            if self.configuration.allow_origins:
                headers['Access-Control-Allow-Origin'] = self.configuration.allow_origins
            if self.configuration.allow_credentials:
                headers['Access-Control-Allow-Credentials'] = self.configuration.allow_credentials.lower()

        return self._serialize_as_single_response(event, status_code, response, headers, merge_with_event=False)


class BaseStepLambdaHandler(BaseLambdaHandler):
    """
    Step lambda always accepts API GW event, does the work, and returns same API GW event,
    with an updated body, as an output.
    """
    websocket_enabled = True

    def _serialize_response(self, event, status_code, response) -> typing.Union[typing.List[dict], dict]:
        return self._serialize_as_single_response(event, status_code, response, merge_with_event=True)
