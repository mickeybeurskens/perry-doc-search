from pathlib import Path
from sqlalchemy.orm import Session
from perry.db.models import Document, User


def create_document(db: Session, file_path: str):
    db_document = Document(file_path=file_path)
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

def get_document(db: Session, document_id: int):
    return db.query(Document).filter(Document.id == document_id).first()

def delete_document(db: Session, document_id: int):
    db_document = get_document(db, document_id)
    if db_document:
        db.delete(db_document)
        db.commit()

def add_user_to_document(db: Session, user_id: int, document_id: int):
    db_user = db.query(User).filter(User.id == user_id).first()
    db_document = get_document(db, document_id)
    if db_user and db_document:
        db_document.users.append(db_user)
        db.commit()
        
def remove_user_from_document(db: Session, user_id: int, document_id: int):
    db_user = db.query(User).filter(User.id == user_id).first()
    db_document = get_document(db, document_id)
    if db_user and db_document:
        db_document.users.remove(db_user)
        db.commit()