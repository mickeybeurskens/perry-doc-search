# test_user_operations.py
from perry.db.operations.users import create_user, get_user
from perry.db.models import pwd_context

def test_create_user(test_db):
    username = "john"
    password = "doe"
    
    created_user = create_user(test_db, username, password)
    
    assert created_user.id is not None
    assert created_user.username == username
    assert pwd_context.verify(password, created_user._password)

def test_get_user(test_db, create_user_in_db):
    username = "arthur"
    password = "dent"
    created_user = create_user_in_db(username, password)
    
    retrieved_user = get_user(test_db, created_user.id)
    
    assert retrieved_user.id == created_user.id
    assert retrieved_user.username == username
    assert pwd_context.verify(password, retrieved_user._password)