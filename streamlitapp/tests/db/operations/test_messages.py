from perry.db.operations.messages import create_message, get_messages_by_user

def test_create_message(test_db, create_user_in_db):
    username = "lancelot"
    password = "blue"
    user = create_user_in_db(test_db, username, password)
    role = "user"
    message_text = "Hello, world!"

    created_message = create_message(test_db, user.id, role, message_text)

    assert created_message.id is not None
    assert created_message.user_id == user.id
    assert created_message.role == role
    assert created_message.message == message_text

def test_get_messages_by_user(test_db, create_user_in_db):
    username = "arthur"
    password = "grail"
    role = "user"
    user = create_user_in_db(test_db, username, password)
    create_message(test_db, user.id, role, "Hello, world!")
    create_message(test_db, user.id, role, "Hello again!")

    messages = get_messages_by_user(test_db, user.id)

    assert len(messages) == 2
    for message in messages:
        assert message.user_id == user.id

