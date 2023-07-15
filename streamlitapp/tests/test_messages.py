import pytest
import datetime
from perry.messages import *


def test_message_index_not_negative():
    """The indexes of messages should never be negative."""
    with pytest.raises(pydantic.ValidationError) as error_info:
      Message(index=-1, user="test_user", message="test message", timestamp=datetime.datetime.now())
    