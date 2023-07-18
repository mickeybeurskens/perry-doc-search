import pydantic
import datetime
import pathlib
from perry.utils import save_pydantic_instance, load_pydantic_instance


class Message(pydantic.BaseModel):
    index: int = pydantic.Field(None, ge=0)
    user: str
    message: str
    timestamp: datetime.datetime = datetime.datetime.now()


class MessageHistory(pydantic.BaseModel):
    index: int = pydantic.Field(None, ge=0)
    messages: list[Message] = None


def get_message_save_dir() -> pathlib.Path:
    path = pathlib.Path(__file__).parent.parent / "storage" / "messages"
    if not path.exists():
        path.mkdir(parents=True)
    return path
    

def save_message_history(message_history: MessageHistory, path: pathlib.Path) -> None:
    file_name = f"message_history_{message_history.index}.json"
    file_path = path / file_name
    save_pydantic_instance(message_history, file_path)


def load_message_history(index: int, path: pathlib.Path) -> MessageHistory:
    file_name = f"message_history_{index}.json"
    file_path = path / file_name
    message_history = load_pydantic_instance(MessageHistory, file_path)
    return message_history
