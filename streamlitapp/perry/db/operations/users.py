from sqlalchemy.orm import Session
from perry.db.models import User


def create_user(db: Session, username: str, password: str) -> int:
    user = User(username=username)
    user.set_password(password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user.id


def get_user(db: Session, user_id: int) -> User:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> User:
    return db.query(User).filter(User.username == username).first()


def update_user(
    db: Session,
    user_id: int,
    username: str = None,
    password: str = None,
    email: str = None,
) -> int:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    if username:
        user.username = username
    if password:
        user.set_password(password)
    if email:
        user.set_email(email)
    db.commit()
    db.refresh(user)
    return user.id


def authenticate_user(db: Session, username: str, password: str) -> int:
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not user.verify_password(password):
        return None
    return user.id
