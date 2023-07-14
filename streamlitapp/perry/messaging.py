import pydantic
import datetime
import json
import pathlib


class Message(pydantic.BaseModel):
    index: int
    user: str
    message: str
    timestamp: datetime.datetime


class MessageHistory(pydantic.BaseModel):
    index: int
    messages: list[Message]
    last_index: int


def get_message_save_dir() -> pathlib.Path:
    path = pathlib.Path(__file__).parent.parent / "storage" / "messages"
    if not path.exists():
        path.mkdir(parents=True)
    return path
    

def save_message_history(message_history: MessageHistory) -> None:
    file_name = f"message_history_{message_history.index}.json"
    file_path = get_message_save_dir() / file_name
    with open(file_path, "w") as f:
        json.dump(message_history.model_dump(mode='json'), f, indent=2)


def load_message_history(index: int) -> MessageHistory:
    file_name = f"message_history_{index}.json"
    file_path = get_message_save_dir() / file_name
    with open(file_path, "r") as f:
        message_history = MessageHistory(**json.load(f))
    return message_history
