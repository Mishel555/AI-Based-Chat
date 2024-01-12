import base64
import dataclasses
import json
import typing
import uuid

from aws_lambda_powertools import Metrics
from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from aws_lambda_powertools.utilities.typing import LambdaContext
from chatbot_cloud_util import util
from chatbot_cloud_util.api_response import (
    EvidenceCreatorErrorResponse,
    EvidenceCreatorResponse,
)
from chatbot_cloud_util.base_lambda import (
    BaseStepLambdaConfiguration,
    BaseStepLambdaHandler,
)
from chatbot_cloud_util.decorators import trace_event, validated_jwt_token_claims
from chatbot_cloud_util.factory import get_ec, get_env
from chatbot_cloud_util.state import (
    AssertionsCreatorState,
    CustomAssertionCreatorState,
    EvidenceCreatorState,
    StatementBasedAssertionsCreatorState,
)
from chatbot_cloud_util.step_request import EvidenceCreatorStepRequest
from chatbot_cloud_util.step_response import EvidenceCreatorStepResponse
from yarl import URL

from .corpus_container import (
    CompatibleLocalCorpusContainerProxy,
    CompatibleRemoteCorpusContainerProxy,
)
from .schema import INPUT_SCHEMA, OUTPUT_SCHEMA

# from aws_xray_sdk.core import patch_all
# patch_all()

metrics = Metrics()
verbosity = get_env('VERBOSITY', int, 0)

util.adjust_logger()


@dataclasses.dataclass
class LambdaConfiguration(BaseStepLambdaConfiguration):
    leap_url: str
    # vector_store_url: str = None


class LambdaHandler(BaseStepLambdaHandler):
    lambda_configuration_class = LambdaConfiguration
    request_class = EvidenceCreatorStepRequest
    existing_state_class = AssertionsCreatorState
    state_class = EvidenceCreatorState
    deserialize_request = True
    metric_name_suffix = 'step-evidence-creator'
    protected_handler = True

    def _deserialize_existing_state(self, **kwargs) -> AssertionsCreatorState:
        if 'statement_id' in kwargs and kwargs['statement_id']:
            return StatementBasedAssertionsCreatorState(**kwargs)
        if 'assertion' in kwargs:
            return CustomAssertionCreatorState(**kwargs)
        raise ValueError(f'Unable to deserialize existing state payload; payload keys: {list(kwargs.keys())[:20]}')

    def _encode_leap_options_params(self, options: list[str]) -> str:
        result = {"seedIds": options}
        return base64.b64encode(json.dumps(result).encode("utf-8")).decode("utf-8")
    
    def _build_leap_url(self, leap_url: typing.Union[URL, str], *openalex_urls: str) -> str:
        ids = [url.split("/")[-1] for url in openalex_urls]
        if isinstance(leap_url, str):
            leap_url = URL(leap_url)
        return leap_url.with_path('search').with_query(
                    {"options": self._encode_leap_options_params(ids)}
                ).human_repr()

    def _handle(self, event: typing.Union[APIGatewayProxyEvent, dict], existing_state: AssertionsCreatorState = None):
        self.logger.info('Evidence creator request')
        state = None
        ws_response = None
        try:
            cc = CompatibleLocalCorpusContainerProxy(
                self.configuration.llm_name,
                **event['stageVariables'],
            )
            cc.index([existing_state.assertion], save_to_disk=False)

            ec = get_ec(self.configuration.llm_name, **event['stageVariables'])
            store_oa_urls = True
            ec.set_evidence(
                existing_state.assertion,
                cc.get_corpus(),
                recency_vs_similarity=1,
                get_metadata=True,
                log_steps=verbosity > 0,
                save_oa_urls=store_oa_urls,
            )
            evidence = ec.get_evidence()
            if store_oa_urls:
                urls_mapping = ec.get_oa_urls()
                for key, value in evidence.items():
                    if isinstance(value, dict) and key in urls_mapping:
                        value['leap_url'] = self._build_leap_url(self.configuration.leap_url, urls_mapping[key])

            response = EvidenceCreatorStepResponse(
                id=uuid.uuid4(),
                chat_id=self.request.chat_id,
                chat_ts=self.request.chat_ts,
                ts=self.now,
            )
            state = self._build_state(
                response,
                assertion_id=existing_state.id,
                evidence=evidence,
                extra=existing_state.extra
            )

            ws_response = EvidenceCreatorResponse(
                id=response.id,
                assertion_id=existing_state.id,
                evidence=evidence,
                chat_id=self.request.chat_id,
                chat_ts=self.request.chat_ts,
                ts=self.now,
                extra=existing_state.extra,
            )
            return 200, response, ws_response, state
        except Exception as e:
            self.logger.exception('Unable to handle request')
            response = EvidenceCreatorErrorResponse(
                assertion_id=existing_state.id,
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
