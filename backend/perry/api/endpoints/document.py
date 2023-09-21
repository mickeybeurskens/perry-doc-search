from fastapi import APIRouter
from perry.db.operations.documents import (
    get_document,
    create_document,
    update_document,
    delete_document,
)
from perry.db.session import DatabaseSessionManager


document_router = APIRouter()
