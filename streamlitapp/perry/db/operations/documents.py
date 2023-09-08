import pathlib
import io
import os
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from perry.db.models import Document, User


def save_file(db_session: Session, bytes_obj: io.BytesIO, suffix: str):
    """Convert bytes object to a saved file on the filesystem and create an entry in the document database."""
    new_doc = Document()
    db_session.add(new_doc)
    db_session.flush()  # Generates the ID without committing the transaction

    try:
        file_path = pathlib.Path(get_file_storage_path(), f"{new_doc.id}.{suffix}")
        new_doc.file_path = str(file_path)
        save_bytes_to_file(bytes_obj, file_path)

        db_session.commit()
    except SQLAlchemyError as sql_e:
        db_session.rollback()
        raise
    except Exception:
        if file_path.is_file():
            os.remove(file_path)
        db_session.rollback()
        raise
    return new_doc


def remove_file(db_session: Session, document_id: int):
    """Remove a document reference and the corresponding file in the file system."""
    try:
        document = get_document(db_session, document_id)
        if document is None:
            raise ValueError("Document not found, cannot remove file based on document ID")

        file_path = pathlib.Path(document.file_path)
        if file_path.is_file():
            os.remove(file_path)

        delete_document(db_session, document_id)

    except Exception as e:
        db_session.rollback()
        raise


def load_file(db_session: Session, document_id: int) -> io.BytesIO:
    """¨Load bytes object from file on the filesystem."""
    file_path = get_document(db_session, document_id).file_path
    return load_bytes_from_file(file_path)


def save_bytes_to_file(bytes_obj: io.BytesIO, file_path: pathlib.Path):
    """Convert bytes object to file on the filesystem."""
    with open(file_path, "wb") as f:
        f.write(bytes_obj.getbuffer())


def load_bytes_from_file(file_path: pathlib.Path) -> io.BytesIO:
    """¨Load bytes object from file on the filesystem."""
    with open(file_path, "rb") as f:
        bytes_obj = io.BytesIO(f.read())
    return bytes_obj


def get_file_storage_path(document_path: pathlib.Path):
    return pathlib.Path(document_path.parent / "storage" / "files")


def create_document(db: Session):
    """Create a new document object in the database."""
    db_document = Document()
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document


def get_document(db: Session, document_id: int):
    """Get a document object from the database."""
    return db.query(Document).filter(Document.id == document_id).first()


def delete_document(db: Session, document_id: int):
    """Delete a document object from the database."""
    db_document = get_document(db, document_id)
    if db_document:
        db.delete(db_document)
        db.commit()


def add_user_to_document(db: Session, user_id: int, document_id: int):
    """Add a user to a document database object."""
    db_user = db.query(User).filter(User.id == user_id).first()
    db_document = get_document(db, document_id)
    if db_user and db_document:
        db_document.users.append(db_user)
        db.commit()


def remove_user_from_document(db: Session, user_id: int, document_id: int):
    """Remove a user from a document database object."""
    db_user = db.query(User).filter(User.id == user_id).first()
    db_document = get_document(db, document_id)
    if db_user and db_document:
        db_document.users.remove(db_user)
        db.commit()


def update_document_file_path(db: Session, document_id: int, new_file_path: str):
    """Update the file path of a document database object."""
    db_document = db.query(Document).filter(Document.id == document_id).first()
    if db_document is None:
        return None
    db_document.file_path = new_file_path
    db.commit()
    db.refresh(db_document)
    return db_document


def update_document_description(db: Session, document_id: int, new_description: str):
    """Update the description of a document database object."""
    db_document = db.query(Document).filter(Document.id == document_id).first()
    if db_document is None:
        return None
    db_document.description = new_description
    db.commit()
    db.refresh(db_document)
    return db_document


def update_document_title(db: Session, document_id: int, new_title: str):
    """Update the title of a document database object."""
    db_document = db.query(Document).filter(Document.id == document_id).first()
    if db_document is None:
        return None
    db_document.title = new_title
    db.commit()
    db.refresh(db_document)
    return db_document
