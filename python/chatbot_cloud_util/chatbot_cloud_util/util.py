import sys
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from dateutil import parser
from loguru import logger
from yarl import URL


def utcnow() -> datetime:
    return datetime.utcnow().replace(tzinfo=timezone.utc)


def parse_ts(value: str) -> datetime:
    return parser.isoparse(value)


def adjust_logger():
    try:
        logger.remove(0)
        logger.add(sys.stderr, format="{time:MMMM D, YYYY > HH:mm:ss} | {level} | {message} | {extra}")
    except ValueError:
        pass

def get_base_url(event: dict, extra_path: Optional[str] = None) -> URL:
    request_context = event['requestContext']
    headers = event['headers']
    host = request_context['domainName']
    protocol = headers['X-Forwarded-Proto']
    url = URL(
        f'{protocol}://{host}/'
    )
    if extra_path is not None:
        url = url.with_path(extra_path)
    return url



def reset_factory():
    for key in ('_ac', '_cc', '_ec', '_sc', '_jwt_key', '_open_ai_key'):
        if key in globals():
            globals()[key] = None


STATE_MACHINE_INTRA_SCHEMA = {}


class AutoName(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name