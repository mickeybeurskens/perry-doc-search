import io
import os
import pathlib
from perry.db.operations.documents import create_document, update_document_file_path, update_document_description, update_document_title, add_user_to_document, delete_document, get_document
from perry.db.session import db_session


def save_file_to_storage(bytes_obj: io.BytesIO, title: str, description: str, user_id: int, suffix: str):
    """Convert bytes object to file on the filesystem."""
    new_doc = create_document(db_session)

    file_path = pathlib.Path(get_file_storage_path(), new_doc.id + "." + suffix)
    update_document_file_path(db_session, new_doc.id, file_path)
    
    update_document_title(db_session, new_doc.id, title)
    update_document_description(db_session, new_doc.id, description)
    add_user_to_document(db_session, user_id, new_doc.id)
    save_bytes_to_file(bytes_obj, file_path)
    
def remove_file_from_storage(document_id: int):
    """Convert bytes object to file on the filesystem."""
    file_path = get_document(db_session, document_id).file_path
    if file_path.is_file():
        os.remove(file_path)
    delete_document(db_session, document_id)
    
def load_file_from_storage(document_id: int) -> io.BytesIO:
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
    return pathlib.Path(document_path.parent / "storage" / "files" )
