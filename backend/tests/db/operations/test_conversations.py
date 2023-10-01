from perry.db.operations.conversations import (
    create_conversation,
    read_conversation,
    update_conversation,
    delete_conversation,
    add_messages_to_conversation,
)
from perry.db.operations.messages import read_message
from perry.db.models import Conversation


def test_create_conversation(test_db):
    conv_id = create_conversation(test_db)
    conv = test_db.query(Conversation).filter_by(id=conv_id).first()
    assert conv is not None


def test_read_conversation(test_db, add_conversation_to_db):
    conv_id = add_conversation_to_db()
    conv = read_conversation(test_db, conv_id)
    assert conv is not None
    assert conv.id == conv_id


def test_update_conversation(test_db, add_conversation_to_db):
    conv_id = add_conversation_to_db()
    updated_conv = update_conversation(test_db, conv_id, 2)
    assert updated_conv is not None
    assert updated_conv.user_id == 2


def test_delete_conversation(test_db, add_conversation_to_db):
    conv_id = add_conversation_to_db()
    assert delete_conversation(test_db, conv_id) is True
    conv = read_conversation(test_db, conv_id)
    assert conv is None


def test_update_nonexistent_conversation(test_db):
    assert update_conversation(test_db, 9999, 1) is None


def test_delete_nonexistent_conversation(test_db):
    assert delete_conversation(test_db, 9999) is None


def test_read_nonexistent_conversation(test_db):
    assert read_conversation(test_db, 9999) is None


def test_add_messages_to_conversation_nonexistent_conversation(test_db):
    assert add_messages_to_conversation(test_db, 9999, [1, 2, 3]) is None


def test_add_messages_to_conversation_nonexistent_message(
    test_db, add_conversation_to_db
):
    conv_id = add_conversation_to_db()
    assert add_messages_to_conversation(test_db, conv_id, [9999]) is None


def test_add_messages_to_conversation_returns_messages(
    test_db, add_conversation_to_db, add_message_to_db
):
    conv_id = add_conversation_to_db()
    message_ids = [add_message_to_db(1), add_message_to_db(2), add_message_to_db(3)]
    conv = add_messages_to_conversation(test_db, conv_id, message_ids)
    conv_message_ids = [message.id for message in conv.messages]
    assert conv is not None
    assert conv_message_ids == message_ids
