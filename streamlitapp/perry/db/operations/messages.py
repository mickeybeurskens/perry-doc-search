# message_operations.py
from sqlalchemy.orm import Session
from perry.db.models import Message

def create_message(db: Session, user_id: int, role: str, message: str):
    message = Message(user_id=user_id, role=role, message=message)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message

def get_messages_by_user(db: Session, user_id: int):
    return db.query(Message).filter(Message.user_id == user_id).all()
