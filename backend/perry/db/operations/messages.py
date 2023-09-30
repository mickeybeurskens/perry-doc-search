# message_operations.py
from sqlalchemy.orm import Session
from perry.db.models import Message


def create_message(db: Session, user_id: int, role: str, message: str):
    message = Message(user_id=user_id, role=role, message=message)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message.id


def read_message(db: Session, message_id: int):
    return db.query(Message).filter(Message.id == message_id).first()


def delete_message(db: Session, message_id: int):
    message = read_message(db, message_id)
    if not message:
        return None
    db.delete(message)
    db.commit()
    return True


def get_messages_by_user(db: Session, user_id: int):
    return db.query(Message).filter(Message.user_id == user_id).all()
