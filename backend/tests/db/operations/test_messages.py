from perry.db.operations.messages import create_message, get_messages_by_user


def test_create_message(test_db, create_user_in_db):
    username = "lancelot"
    password = "blue"
    user_id = create_user_in_db(username, password)
    role = "user"
    message_text = "Hello, world!"

    created_message = create_message(test_db, user_id, role, message_text)

    assert created_message.id is not None
    assert created_message.user_id == user_id
    assert created_message.role == role
    assert created_message.message == message_text


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
