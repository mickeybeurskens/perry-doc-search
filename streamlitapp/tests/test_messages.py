import pytest
import datetime
import tempfile
from perry.messages import *


def test_message_index_not_negative():
    """The indexes of messages should never be negative."""
    with pytest.raises(pydantic.ValidationError) as error_info:
      Message(index=-1, user="test_user", message="test message", timestamp=datetime.datetime.now())

def test_message_history_index_not_negative():
    """The indexes of message histories should never be negative."""
    messages = [
      Message(index=0, user="test_user", message="test message", timestamp=datetime.datetime.now()),
      Message(index=1, user="test_user_2", message="test message", timestamp=datetime.datetime.now()),
      Message(index=4, user="test_user", message="test message", timestamp=datetime.datetime.now())
    ]
    with pytest.raises(pydantic.ValidationError) as error_info:
      MessageHistory(index=-1, messages=messages)

def test_message_history_saved_and_loaded_same():
  """A message history that is saved should also be loaded back correctly."""
  messages = [
    Message(index=0, user="test_user", message="test message", timestamp=datetime.datetime.now()),
    Message(index=1, user="test_user_2", message="test message", timestamp=datetime.datetime.now()),
    Message(index=4, user="test_user", message="test message", timestamp=datetime.datetime.now())
  ]
  message_history = MessageHistory(index=0, messages=messages)
  with tempfile.TemporaryDirectory() as tmp_dir_name:
    tmp_dir_path = pathlib.Path(tmp_dir_name)
    save_message_history(message_history, tmp_dir_path)
    loaded_history = load_message_history(0, tmp_dir_path)
    assert message_history == loaded_history




