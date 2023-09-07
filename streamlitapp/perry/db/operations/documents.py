from sqlalchemy.orm import Session
from perry.db.models import Document, User


def create_document(db: Session):
    db_document = Document()
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

def update_document_file_path(db: Session, document_id: int, new_file_path: str):
    db_document = db.query(Document).filter(Document.id == document_id).first()
    if db_document is None:
        return None
    db_document.file_path = new_file_path
    return db_document

def update_document_description(db: Session, document_id: int, new_description: str):
    db_document = db.query(Document).filter(Document.id == document_id).first()
    if db_document is None:
        return None
    db_document.description = new_description
    db.commit()
    db.refresh(db_document)
    return db_document

def update_document_title(db: Session, document_id: int, new_title: str):
    db_document = db.query(Document).filter(Document.id == document_id).first()
    if db_document is None:
        return None
    db_document.title = new_title
    db.commit()
    db.refresh(db_document)
    return db_document