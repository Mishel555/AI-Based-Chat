import abc
import dataclasses
import uuid
from datetime import datetime

import chatbot_cloud_util.util as util
from chatbot_cloud_util.mixins import JsonSerializableDataclass, WithError


@dataclasses.dataclass
class Response(abc.ABC, JsonSerializableDataclass):
    ts: datetime

    def __post_init__(self):
        if type(self.ts) != datetime:
            self.ts = util.parse_ts(str(self.ts))


@dataclasses.dataclass
class ChatResponse(Response):
    chat_id: uuid.UUID
    chat_ts: datetime

    def __post_init__(self):
        super().__post_init__()
        if type(self.chat_id) != uuid.UUID:
            self.chat_id = uuid.UUID(str(self.chat_id))
        if type(self.chat_ts) != datetime:
            self.chat_ts = util.parse_ts(str(self.chat_ts))


@dataclasses.dataclass
class ErrorResponse(Response, WithError):
    pass


@dataclasses.dataclass
class ErrorChatResponse(ChatResponse, WithError):
    pass
