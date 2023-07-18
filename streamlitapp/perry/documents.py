import io
import pydantic
import pathlib
from datetime import datetime
from perry.utils import save_pydantic_instance, load_pydantic_instance


class DocumentMetadata(pydantic.BaseModel):
    title: str
    summary: str
    file_path: pathlib.Path
    date: datetime = datetime.now()


def save_bytes_to_file(bytes_obj: io.BytesIO, file_path: pathlib.Path):
    """Convert bytes object to file on the filesystem."""
    with open(file_path, "wb") as f:
        f.write(bytes_obj.getbuffer())


def load_bytes_from_file(file_path: pathlib.Path) -> io.BytesIO:
    """¨Load bytes object from file on the filesystem."""
    with open(file_path, "rb") as f:
        bytes_obj = io.BytesIO(f.read())
    return bytes_obj


def metadata_postfix() -> str:
    return "_meta.json"


def get_metadata_filepath(document_path: pathlib.Path):
    return pathlib.Path(document_path.parent) / "metadata" / pathlib.Path(document_path.stem + metadata_postfix())


def save_document_metadata(metadata: DocumentMetadata):
    """Save document metadata to a json file."""
    meta_file_path = get_metadata_filepath(metadata.file_path)
    if not meta_file_path.parent.exists():
        meta_file_path.parent.mkdir(parents=True)
    save_pydantic_instance(metadata, get_metadata_filepath(metadata.file_path))


def load_document_metadata(filename: pathlib.Path):
    """Load document metadata from a json file."""
    return load_pydantic_instance(DocumentMetadata, filename)


def load_metadata_from_document_path(document_path: pathlib.Path):
    """Load document metadata from a json file from the document name."""
    return load_pydantic_instance(DocumentMetadata, get_metadata_filepath(document_path))


def save_document(document: io.BytesIO, metadata: DocumentMetadata):
    """Save a document to the filesystem."""
    save_bytes_to_file(document, metadata.file_path)
    save_document_metadata(metadata)


def load_document(document_path: pathlib.Path):
    """Load a document from the filesystem.
    
    args:
        document_path: pathlib.Path
    returns:
        document_bytes: io.BytesIO
        metadata: DocumentMetadata
    """
    document_bytes = load_bytes_from_file(document_path)
    metadata = load_metadata_from_document_path(document_path)
    return document_bytes, metadata
