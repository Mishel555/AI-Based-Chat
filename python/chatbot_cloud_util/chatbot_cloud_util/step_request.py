import dataclasses
import uuid

from chatbot_cloud_util.request import ChatRequest


@dataclasses.dataclass
class StepRequest(ChatRequest):
    id: uuid.UUID

    def __post_init__(self):
        super().__post_init__()
        if type(self.id) != uuid.UUID:
            self.id = uuid.UUID(str(self.id))


@dataclasses.dataclass
class ObfuscatorStepRequest(StepRequest):
    pass


@dataclasses.dataclass
class StatementCreatorStepRequest(StepRequest):
    pass


@dataclasses.dataclass
class TaskTokenNotificatorStepRequest(StepRequest):
    pass


@dataclasses.dataclass
class AssertionsCreatorStepRequest(StepRequest):
    pass


@dataclasses.dataclass
class EvidenceCreatorStepRequest(StepRequest):
    pass
