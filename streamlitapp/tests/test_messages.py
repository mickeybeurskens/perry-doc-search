import pytest
import datetime
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
