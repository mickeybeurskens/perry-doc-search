from perry.db.operations.messages import (
    create_message,
    get_messages_by_user,
    read_message,
    delete_message,
)


def test_create_message(test_db, create_user_in_db):
    username = "lancelot"
    password = "blue"
    user_id = create_user_in_db(username, password)
    role = "user"
    message_text = "Hello, world!"

    created_message_id = create_message(test_db, user_id, role, message_text)
    created_message = read_message(test_db, created_message_id)

    assert created_message.id is not None
    assert created_message.user_id == user_id
    assert created_message.role == role
    assert created_message.message == message_text


def test_read_message_does_not_return_nonexistent_message(test_db):
    nonexistent_message_id = 9999

    message = read_message(test_db, nonexistent_message_id)

    assert message is None


def test_read_message_returns_message(test_db, create_user_in_db):
    username = "lancelot"
    password = "blue"
    user_id = create_user_in_db(username, password)
    role = "user"
    message_text = "Hello, world!"
    message_id = create_message(test_db, user_id, role, message_text)

    message = read_message(test_db, message_id)

    assert message.id == message_id
    assert message.user_id == user_id
    assert message.role == role
    assert message.message == message_text


def test_delete_message_does_not_delete_nonexistent_message(test_db):
    nonexistent_message_id = 9999

    message_deleted = read_message(test_db, nonexistent_message_id)

    assert message_deleted is None


def test_delete_message_deletes_message(test_db, create_user_in_db):
    username = "lancelot"
    password = "blue"
    user_id = create_user_in_db(username, password)
    role = "user"
    message_text = "Hello, world!"
    message_id = create_message(test_db, user_id, role, message_text)

    message_deleted = read_message(test_db, message_id)

    assert message_deleted is not None

    delete_message(test_db, message_id)

    message_deleted = read_message(test_db, message_id)

    assert message_deleted is None


def test_get_messages_by_user(test_db, create_user_in_db):
    username = "arthur"
    password = "grail"
    role = "user"
    user_id = create_user_in_db(username, password)
    create_message(test_db, user_id, role, "Hello, world!")
    create_message(test_db, user_id, role, "Hello again!")

    messages = get_messages_by_user(test_db, user_id)

    assert len(messages) == 2
    for message in messages:
        assert message.user_id == user_id
