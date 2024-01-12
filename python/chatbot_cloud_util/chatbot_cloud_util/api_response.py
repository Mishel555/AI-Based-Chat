import abc
import dataclasses
import typing
import uuid

from chatbot_cloud_util.mixins import WithError
from chatbot_cloud_util.response import ChatResponse, Response


@dataclasses.dataclass
class ConnectResponse(Response):
    pass


@dataclasses.dataclass
class StartChatResponse(Response):
    id: uuid.UUID

    def __post_init__(self):
        super().__post_init__()
        if type(self.id) != uuid.UUID:
            self.id = uuid.UUID(str(self.id))


class WebSocketChatResponseTypeSetOnceDescriptor:
    def __init__(self, value):
        self.__value = value

    def __set_name__(self, owner, attr):
        self.owner = owner.__name__
        self.attr = attr

    def __get__(self, instance, owner):
        return self.__value

    def __set__(self, instance, value):
        raise AttributeError(f"{self.owner}.{self.attr} cannot be set.")


@dataclasses.dataclass
class WebSocketChatResponse(ChatResponse):
    extra: typing.Any

    @property
    @abc.abstractmethod
    def type(self):
        pass

    def to_safe_dict(self):
        d = super()._to_safe_dict(dataclasses.asdict(self))
        if 'extra' in d and not d['extra']:
            del d['extra']
        return d


@dataclasses.dataclass
class SendTaskResponse(WebSocketChatResponse):
    type: str = dataclasses.field(default=WebSocketChatResponseTypeSetOnceDescriptor('send_task'),
                                  init=False, repr=False)
    id: uuid.UUID

    def __post_init__(self):
        super().__post_init__()
        if type(self.id) != uuid.UUID:
            self.id = uuid.UUID(str(self.id))


@dataclasses.dataclass
class SendTaskErrorResponse(WebSocketChatResponse, WithError):
    type: str = dataclasses.field(default=WebSocketChatResponseTypeSetOnceDescriptor('send_task'),
                                  init=False, repr=False)


@dataclasses.dataclass
class TaskTokenResponse(WebSocketChatResponse):
    type: str = dataclasses.field(default=WebSocketChatResponseTypeSetOnceDescriptor('task_token'),
                                  init=False, repr=False)
    id: uuid.UUID
    task_token: str
    step_type: str

    def __post_init__(self):
        super().__post_init__()
        if type(self.id) != uuid.UUID:
            self.id = uuid.UUID(str(self.id))


@dataclasses.dataclass
class TaskTokenErrorResponse(WebSocketChatResponse, WithError):
    type: str = dataclasses.field(default=WebSocketChatResponseTypeSetOnceDescriptor('task_token'),
                                  init=False, repr=False)
    id: uuid.UUID
    step_type: str

    def __post_init__(self):
        super().__post_init__()
        if type(self.id) != uuid.UUID:
            self.id = uuid.UUID(str(self.id))


@dataclasses.dataclass
class HumanInputResponse(WebSocketChatResponse):
    type: str = dataclasses.field(default=WebSocketChatResponseTypeSetOnceDescriptor('human_input'),
                                  init=False, repr=False)
    id: uuid.UUID

    def __post_init__(self):
        super().__post_init__()
        if type(self.id) != uuid.UUID:
            self.id = uuid.UUID(str(self.id))


@dataclasses.dataclass
class HumanInputErrorResponse(WebSocketChatResponse, WithError):
    type: str = dataclasses.field(default=WebSocketChatResponseTypeSetOnceDescriptor('human_input'),
                                  init=False, repr=False)


@dataclasses.dataclass
class CustomAssertionResponse(WebSocketChatResponse):
    type: str = dataclasses.field(default=WebSocketChatResponseTypeSetOnceDescriptor('custom_assertion'),
                                  init=False, repr=False)
    id: uuid.UUID
    statement_id: typing.Optional[uuid.UUID] = None

    def __post_init__(self):
        super().__post_init__()
        if type(self.id) != uuid.UUID:
            self.id = uuid.UUID(str(self.id))
        if self.statement_id and type(self.statement_id) != uuid.UUID:
            self.statement_id = uuid.UUID(str(self.statement_id))


@dataclasses.dataclass
class CustomAssertionErrorResponse(WebSocketChatResponse, WithError):
    type: str = dataclasses.field(default=WebSocketChatResponseTypeSetOnceDescriptor('custom_assertion'),
                                  init=False, repr=False)
    statement_id: typing.Optional[uuid.UUID] = None

    def __post_init__(self):
        super().__post_init__()
        if self.statement_id and type(self.statement_id) != uuid.UUID:
            self.statement_id = uuid.UUID(str(self.statement_id))


@dataclasses.dataclass
class StatementCreatorResponse(WebSocketChatResponse):
    type: str = dataclasses.field(default=WebSocketChatResponseTypeSetOnceDescriptor('statement'),
                                  init=False, repr=False)
    id: uuid.UUID
    human_input_id: uuid.UUID
    statement: str

    def __post_init__(self):
        super().__post_init__()
        if type(self.id) != uuid.UUID:
            self.id = uuid.UUID(str(self.id))
        if type(self.human_input_id) != uuid.UUID:
            self.human_input_id = uuid.UUID(str(self.human_input_id))


@dataclasses.dataclass
class StatementCreatorErrorResponse(WebSocketChatResponse, WithError):
    type: str = dataclasses.field(default=WebSocketChatResponseTypeSetOnceDescriptor('statement'),
                                  init=False, repr=False)
    human_input_id: uuid.UUID

    def __post_init__(self):
        super().__post_init__()
        if type(self.human_input_id) != uuid.UUID:
            self.human_input_id = uuid.UUID(str(self.human_input_id))


@dataclasses.dataclass
class AssertionsCreatorResponse(WebSocketChatResponse):
    type: str = dataclasses.field(default=WebSocketChatResponseTypeSetOnceDescriptor('assertions'),
                                  init=False, repr=False)
    ids: typing.Tuple[uuid.UUID]
    statement_id: uuid.UUID
    assertions: typing.Tuple[str]

    def __post_init__(self):
        super().__post_init__()
        if self.ids:
            self.ids = tuple([
                uuid.UUID(str(id)) if type(id) != uuid.UUID else id
                for id in self.ids
            ])
        if type(self.statement_id) != uuid.UUID:
            self.statement_id = uuid.UUID(str(self.statement_id))


@dataclasses.dataclass
class AssertionsCreatorErrorResponse(WebSocketChatResponse, WithError):
    type: str = dataclasses.field(default=WebSocketChatResponseTypeSetOnceDescriptor('assertions'),
                                  init=False, repr=False)
    statement_id: uuid.UUID

    def __post_init__(self):
        super().__post_init__()
        if type(self.statement_id) != uuid.UUID:
            self.statement_id = uuid.UUID(str(self.statement_id))


@dataclasses.dataclass
class EvidenceCreatorResponse(WebSocketChatResponse):
    type: str = dataclasses.field(default=WebSocketChatResponseTypeSetOnceDescriptor('evidence'),
                                  init=False, repr=False)
    id: uuid.UUID
    assertion_id: uuid.UUID
    evidence: typing.Union[str, dict]

    def __post_init__(self):
        super().__post_init__()
        if type(self.id) != uuid.UUID:
            self.id = uuid.UUID(str(self.id))
        if type(self.assertion_id) != uuid.UUID:
            self.assertion_id = uuid.UUID(str(self.assertion_id))


@dataclasses.dataclass
class EvidenceCreatorErrorResponse(WebSocketChatResponse, WithError):
    type: str = dataclasses.field(default=WebSocketChatResponseTypeSetOnceDescriptor('evidence'),
                                  init=False, repr=False)
    assertion_id: uuid.UUID

    def __post_init__(self):
        super().__post_init__()
        if type(self.assertion_id) != uuid.UUID:
            self.assertion_id = uuid.UUID(str(self.assertion_id))
