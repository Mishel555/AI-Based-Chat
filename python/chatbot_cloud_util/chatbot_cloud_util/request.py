import abc
import base64
import dataclasses
import json
import uuid
from datetime import datetime
from inspect import signature

import chatbot_cloud_util.util as util
from chatbot_cloud_util.mixins import JsonSerializableDataclass


@dataclasses.dataclass
class Request(abc.ABC, JsonSerializableDataclass):
    ts: datetime

    @classmethod
    def from_event(cls, event: dict, parent_key='body', deserialize_container=False, **kwargs):
        cls_fields = {field for field in signature(cls).parameters}

        container = event.get(parent_key, {}) if parent_key else event
        if event.get('isBase64Encoded'):
            container = base64.b64decode(container).decode('utf-8')
        container = json.loads(container) if deserialize_container else container
        container_values = {name: val for name, val in container.items() if name in cls_fields}

        return cls(**{**container_values, **kwargs})

    def __post_init__(self):
        if type(self.ts) != datetime:
            self.ts = util.parse_ts(str(self.ts))


@dataclasses.dataclass
class ChatRequest(Request):
    chat_id: uuid.UUID
    chat_ts: datetime

    def __post_init__(self):
        super().__post_init__()
        if type(self.chat_id) != uuid.UUID:
            self.chat_id = uuid.UUID(str(self.chat_id))
        if type(self.chat_ts) != datetime:
            self.chat_ts = util.parse_ts(str(self.chat_ts))
