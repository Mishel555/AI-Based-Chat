import dataclasses
import uuid

from chatbot_cloud_util.response import ChatResponse


@dataclasses.dataclass
class StepResponse(ChatResponse):
    id: uuid.UUID

    def __post_init__(self):
        super().__post_init__()
        if type(self.id) != uuid.UUID:
            self.id = uuid.UUID(str(self.id))


@dataclasses.dataclass
class ObfuscatorStepResponse(StepResponse):
    pass


@dataclasses.dataclass
class StatementCreatorStepResponse(StepResponse):
    pass


@dataclasses.dataclass
class TaskTokenNotificatorStepResponse(StepResponse):
    pass


@dataclasses.dataclass
class AssertionsCreatorStepResponse(StepResponse):
    pass


@dataclasses.dataclass
class EvidenceCreatorStepResponse(StepResponse):
    pass
