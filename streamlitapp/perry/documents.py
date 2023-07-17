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


def save_bytes_to_file(bytes_obj: io.BytesIO, filename):
    """Convert bytes object to file on the filesystem."""
    with open(filename, "wb") as f:
        f.write(bytes_obj.getbuffer())


def load_bytes_from_file(filename) -> io.BytesIO:
    """¨Load bytes object from file on the filesystem."""
    with open(filename, "rb") as f:
        bytes_obj = io.BytesIO(f.read())
    return bytes_obj


def metadata_postfix() -> str:
    return "_meta.json"


def get_metadata_filepath(document_path: pathlib.Path):
    return pathlib.Path(document_path.parent) / pathlib.Path(document_path.stem + metadata_postfix())


def save_document_metadata(metadata: DocumentMetadata):
    """Save document metadata to a json file."""
    save_pydantic_instance(metadata, get_metadata_filepath(metadata.file_path))


def load_document_metadata(filename: pathlib.Path):
    """Load document metadata from a json file."""
    return load_pydantic_instance(DocumentMetadata, filename)


def load_metadata_from_document_path(document_path: pathlib.Path):
    """Load document metadata from a json file from the document name."""
    return load_pydantic_instance(DocumentMetadata, get_metadata_filepath(document_path))