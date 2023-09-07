from sqlalchemy.orm import Session
from perry.db.models import User

def create_user(db: Session, username: str, password: str):
    user = User(username=username)
    user.set_password(password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()
