import json
import typing
import uuid
from collections import deque
from pathlib import Path

from chatbot_cloud_util.util import utcnow
from langchain.schema import (
    AIMessage,
    BaseChatMessageHistory,
    BaseMessage,
    HumanMessage,
    _message_to_dict,
    messages_from_dict,
)

from .aws_api import read_str_from_s3, s3, write_str_to_s3


class S3ChatMessageHistory(BaseChatMessageHistory):
    BUFFER_LIMIT = 100

    def __init__(self, bucket_name: str, bucket_object_prefix_tpl: str):
        self.bucket_name = bucket_name
        self._object_prefix = bucket_object_prefix_tpl
        self.client = s3()
        self.buffer: deque[BaseMessage] = deque(maxlen=self.BUFFER_LIMIT)

    def _populate_buffer_from_s3(self) -> None:
        response = self.client.list_objects(Bucket=self.bucket_name, Prefix=self._object_prefix)
        messages_path = response.get('Contents', [])
        messages = [
            json.loads(
                read_str_from_s3(
                    self.bucket_name,
                    message['Key']
                )
            ) for message in messages_path
        ]
        self.buffer.extend(
            sorted(
                    messages_from_dict(messages),
                    key=lambda x: x.additional_kwargs['dt']
                )[:self.BUFFER_LIMIT]
            )

    @property
    def messages(self) -> typing.List[BaseMessage]:
        if len(self.buffer) == 0:
            self._populate_buffer_from_s3()
        return list(self.buffer)

    def _store_message(self, message_path: str, message: BaseMessage) -> None:
        message.additional_kwargs['dt'] = utcnow().isoformat()
        write_str_to_s3(self.bucket_name, message_path, json.dumps(_message_to_dict(message)))
        self.buffer.append(message)
        if len(self.buffer) >= self.BUFFER_LIMIT:
            self.buffer.popleft()

    def add_user_message(self, message: str) -> None:
        message = HumanMessage(content=message)
        file_name = f'user_message:{uuid.uuid4().__str__()}.json'
        message_path = (Path(self._object_prefix) / Path(file_name)).as_posix()
        self._store_message(message_path, message)

    def add_ai_message(self, message: str) -> None:
        message = AIMessage(content=message)
        file_name = f'ai_response:{uuid.uuid4().__str__()}.json'
        message_path = (Path(self._object_prefix) / Path(file_name)).as_posix()
        self._store_message(message_path, message)

    def clear(self) -> None:
        ...