import dataclasses
import typing
import uuid

from chatbot_cloud_util.request import ChatRequest, Request


@dataclasses.dataclass
class ConnectRequest(Request):
    pass


@dataclasses.dataclass
class StartChatRequest(Request):
    pass


@dataclasses.dataclass
class HumanInputRequest(ChatRequest):
    human_input: str
    extra: typing.Any
    obfuscate: bool = True

    def __post_init__(self):
        super().__post_init__()
        if type(self.obfuscate) != bool:
            self.obfuscate = str(self.obfuscate).lower() == 'true'


@dataclasses.dataclass
class CustomAssertionRequest(ChatRequest):
    assertion: str
    extra: typing.Any
    statement_id: typing.Optional[uuid.UUID] = None

    def __post_init__(self):
        super().__post_init__()
        if self.statement_id and type(self.statement_id) != uuid.UUID:
            self.statement_id = uuid.UUID(str(self.statement_id))


@dataclasses.dataclass
class SendTaskRequest(ChatRequest):
    id: uuid.UUID
    task_token: str

    def __post_init__(self):
        super().__post_init__()
        if type(self.id) != uuid.UUID:
            self.id = uuid.UUID(str(self.id))
