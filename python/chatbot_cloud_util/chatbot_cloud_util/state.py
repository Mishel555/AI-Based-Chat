import abc
import dataclasses
import typing
import uuid
from datetime import datetime

import chatbot_cloud_util.util as util
from chatbot_cloud_util.api_request import (
    CustomAssertionRequest,
    HumanInputRequest,
    StartChatRequest,
)
from chatbot_cloud_util.api_response import (
    CustomAssertionResponse,
    HumanInputResponse,
    StartChatResponse,
)
from chatbot_cloud_util.mixins import JsonSerializableDataclass
from chatbot_cloud_util.request import Request
from chatbot_cloud_util.response import Response
from chatbot_cloud_util.step_request import (
    AssertionsCreatorStepRequest,
    EvidenceCreatorStepRequest,
    ObfuscatorStepRequest,
    StatementCreatorStepRequest,
)
from chatbot_cloud_util.step_response import (
    AssertionsCreatorStepResponse,
    EvidenceCreatorStepResponse,
    ObfuscatorStepResponse,
    StatementCreatorStepResponse,
)


@dataclasses.dataclass
class State(abc.ABC, JsonSerializableDataclass):
    id: uuid.UUID
    user: str
    ts: datetime

    @classmethod
    def build_state(cls, *args, request: Request, response: Response, user: str, **kwargs):
        raise

    def __post_init__(self):
        if type(self.id) != uuid.UUID:
            self.id = uuid.UUID(str(self.id))
        if type(self.ts) != datetime:
            self.ts = util.parse_ts(str(self.ts))


@dataclasses.dataclass
class ChatState(State):
    chat_id: uuid.UUID
    chat_ts: datetime
    extra: typing.Any

    def __post_init__(self):
        super().__post_init__()
        if type(self.chat_id) != uuid.UUID:
            self.chat_id = uuid.UUID(str(self.chat_id))
        if type(self.chat_ts) != datetime:
            self.chat_ts = util.parse_ts(str(self.chat_ts))


@dataclasses.dataclass
class StartChatState(ChatState):
    @classmethod
    def build_state(cls, *args,
                    request: StartChatRequest,
                    response: StartChatResponse,
                    user: str, **kwargs):
        return StartChatState(id=response.id, chat_id=response.id, user=user, chat_ts=response.ts, ts=response.ts,
                              extra=None, **kwargs)


@dataclasses.dataclass
class HumanInputState(ChatState):
    human_input: str
    obfuscate: bool

    @classmethod
    def build_state(cls, *args,
                    request: HumanInputRequest,
                    response: HumanInputResponse,
                    user: str, **kwargs):
        return HumanInputState(
            id=response.id, chat_id=response.chat_id, user=user, chat_ts=response.chat_ts, ts=response.ts, **kwargs)


@dataclasses.dataclass
class ObfuscatorState(ChatState):
    human_input_id: uuid.UUID
    obfuscated: str

    @classmethod
    def build_state(cls, *args,
                    request: ObfuscatorStepRequest,
                    response: ObfuscatorStepResponse,
                    user: str, **kwargs):
        return ObfuscatorState(
            id=response.id, chat_id=response.chat_id, user=user, chat_ts=response.chat_ts, ts=response.ts, **kwargs)

    def __post_init__(self):
        super().__post_init__()
        if type(self.human_input_id) != uuid.UUID:
            self.human_input_id = uuid.UUID(str(self.human_input_id))


@dataclasses.dataclass
class StatementCreatorState(ChatState):
    human_input_id: uuid.UUID
    obfuscator_id: uuid.UUID
    statement: str

    @classmethod
    def build_state(cls, *args,
                    request: StatementCreatorStepRequest,
                    response: StatementCreatorStepResponse,
                    user: str, **kwargs):
        return StatementCreatorState(
            id=response.id, chat_id=response.chat_id, user=user, chat_ts=response.chat_ts, ts=response.ts, **kwargs)

    def __post_init__(self):
        super().__post_init__()
        if type(self.human_input_id) != uuid.UUID:
            self.human_input_id = uuid.UUID(str(self.human_input_id))
        if type(self.obfuscator_id) != uuid.UUID:
            self.obfuscator_id = uuid.UUID(str(self.obfuscator_id))


@dataclasses.dataclass
class AssertionsCreatorState(ChatState):
    assertion: str

    @classmethod
    def build_state(cls, *args,
                    request: AssertionsCreatorStepRequest,
                    response: AssertionsCreatorStepResponse,
                    user: str, **kwargs):
        return AssertionsCreatorState(
            id=response.id, chat_id=response.chat_id, user=user, chat_ts=response.chat_ts, ts=response.ts,
            extra=None, **kwargs)


@dataclasses.dataclass
class StatementBasedAssertionsCreatorState(AssertionsCreatorState):
    statement_id: uuid.UUID

    @classmethod
    def build_state(cls, *args,
                    request: AssertionsCreatorStepRequest,
                    response: AssertionsCreatorStepResponse,
                    user: str, **kwargs):
        return StatementBasedAssertionsCreatorState(
            id=response.id, chat_id=response.chat_id, user=user, chat_ts=response.chat_ts, ts=response.ts,
            extra=None, **kwargs)

    def __post_init__(self):
        super().__post_init__()
        if type(self.statement_id) != uuid.UUID:
            self.statement_id = uuid.UUID(str(self.statement_id))


@dataclasses.dataclass
class CustomAssertionCreatorState(AssertionsCreatorState):
    assertion: str
    statement_id: typing.Optional[uuid.UUID] = None

    def __post_init__(self):
        super().__post_init__()
        if self.statement_id and type(self.statement_id) != uuid.UUID:
            self.statement_id = uuid.UUID(str(self.statement_id))

    @classmethod
    def build_state(cls, *args,
                    request: CustomAssertionRequest,
                    response: CustomAssertionResponse,
                    user: str, **kwargs):
        return CustomAssertionCreatorState(
            id=response.id, chat_id=response.chat_id, user=user, chat_ts=response.chat_ts, ts=response.ts, **kwargs)


@dataclasses.dataclass
class EvidenceCreatorState(ChatState):
    assertion_id: uuid.UUID
    evidence: str

    @classmethod
    def build_state(cls, *args,
                    request: EvidenceCreatorStepRequest,
                    response: EvidenceCreatorStepResponse,
                    user: str, **kwargs):
        return EvidenceCreatorState(
            id=response.id, chat_id=response.chat_id, user=user, chat_ts=response.chat_ts, ts=response.ts, **kwargs)

    def __post_init__(self):
        super().__post_init__()
        if type(self.assertion_id) != uuid.UUID:
            self.assertion_id = uuid.UUID(str(self.assertion_id))
