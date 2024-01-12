import dataclasses
import typing

from aws_lambda_powertools import Metrics
from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from aws_lambda_powertools.utilities.typing import LambdaContext
from chatbot_cloud_util import util
from chatbot_cloud_util.api_request import ConnectRequest
from chatbot_cloud_util.api_response import ConnectResponse
from chatbot_cloud_util.base_lambda import (
    BaseApiLambdaHandler,
    BaseWsApiLambdaConfiguration,
)
from chatbot_cloud_util.decorators import (
    handle_exceptions,
    trace_event,
    ws_login_required,
)
from chatbot_cloud_util.response import ErrorResponse
from chatbot_cloud_util.state import State

from .schema import INPUT_SCHEMA, OUTPUT_SCHEMA

# from aws_xray_sdk.core import patch_all
# patch_all()

metrics = Metrics()

util.adjust_logger()


@dataclasses.dataclass
class LambdaConfiguration(BaseWsApiLambdaConfiguration):
    pass


class LambdaHandler(BaseApiLambdaHandler):
    lambda_configuration_class = LambdaConfiguration
    request_class = ConnectRequest
    deserialize_request = True
    metric_name_suffix = 'ws-api'
    protected_handler = True

    def _to_request(self, event: typing.Union[APIGatewayProxyEvent, dict]):
        return ConnectRequest(ts=util.utcnow())

    def _handle(self, event: typing.Union[APIGatewayProxyEvent, dict], existing_state: State = None):
        route = event['requestContext']['routeKey']
        connection_id = event['requestContext']['connectionId']

        self.logger.bind(route=route, connection_id=connection_id)
        self.logger.info('WS connection request')

        state = None
        ws_response = None
        try:
            # import boto3
            # dynamodb = boto3.client('dynamodb')

            # TODO: for now we do not need to broadcast events to all WS subscribers,
            #  therefore not persisting connections
            if route == '$connect':
                pass
            #     # dynamodb.put_item(
            #     #     TableName=configuration.connections_table,
            #     #     Item={'connection_id': {'S': connection_id}}
            #     # )
            elif route == '$disconnect':
                pass
            #     # dynamodb.delete_item(
            #     #     TableName=configuration.connections_table,
            #     #     Key={'connection_id': {'S': connection_id}}
            #     # )
            else:
                return 400, ErrorResponse(error='Unknown route specified', ts=self.now), ws_response, state

            response = ConnectResponse(ts=self.now)

            return 200, response, ws_response, state
        except Exception as e:
            self.logger.exception('Unable to handle request')
            response = ErrorResponse(error=str(e), ts=self.now)
            return self._to_status_code(e), response, ws_response, state


@metrics.log_metrics
# @validator(inbound_schema=INPUT_SCHEMA, outbound_schema=OUTPUT_SCHEMA)
@trace_event
@handle_exceptions
@ws_login_required
def lambda_handler(event: dict, context: LambdaContext, claims: dict) -> dict:
    return LambdaHandler(now=util.utcnow()).handle(event, context, claims, metrics)
