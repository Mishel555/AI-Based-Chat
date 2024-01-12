import dataclasses
import json
import typing
import uuid
from contextlib import contextmanager
from datetime import datetime
from time import perf_counter_ns

import botocore.exceptions
from aws_lambda_powertools import Metrics
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from chatbot_cloud_util.aws_api import apigw_mgmt


@dataclasses.dataclass
class WithError:
    error: str


class JsonSerializableDataclass:
    def to_json(self):
        return json.dumps(self.to_safe_dict())

    def to_safe_dict(self):
        return self._to_safe_dict(dataclasses.asdict(self))

    def _to_safe_dict(self, o):
        if isinstance(o, dict):
            return {k: self._to_safe_dict(v) for k, v in o.items()}
        elif isinstance(o, list) or isinstance(o, tuple):
            return [self._to_safe_dict(v) for v in o]
        elif isinstance(o, datetime):
            return o.isoformat()
        elif isinstance(o, uuid.UUID):
            return str(o)
        else:
            return o


class MeasurableApiGatewayEvent:
    @contextmanager
    def _measure_time(self, event: typing.Union[APIGatewayProxyEvent, dict],
                      metrics: Metrics, name: str, unit: MetricUnit = MetricUnit.Milliseconds) -> None:
        start = end = perf_counter_ns()
        metric_name = f'{event["requestContext"]["stage"]}-{name}'
        try:
            yield
            end = perf_counter_ns()
            metrics.add_metric(metric_name, unit, value=(end - start) / 1e+6)
        except:
            end = perf_counter_ns()
            metrics.add_metric(f'{metric_name}-failed', unit, value=(end - start) / 1e+6)
            raise


class WebSocketEnabledApiGatewayEvent:
    def _send_ws_message(self, event: typing.Union[APIGatewayProxyEvent, dict],
                         message: str, ignore_stale_conn: bool = True) -> None:
        connection_id = event['requestContext']['connectionId']
        try:
            apigw_mgmt(**event['requestContext']).post_to_connection(Data=message, ConnectionId=connection_id)
        except botocore.exceptions.ClientError as error:
            if error.response['Error']['Code'] == 'GoneException':
                if ignore_stale_conn:
                    self.logger.warning('WS connection is stale, ignoring', connection_id=connection_id)
                else:
                    raise
