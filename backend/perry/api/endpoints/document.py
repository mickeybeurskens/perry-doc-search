from typing import Annotated
from fastapi import APIRouter, Depends
from perry.api.authentication import get_current_user
from perry.api.schemas import APIDocument
from perry.db.operations.documents import (
    get_document,
    create_document,
    update_document,
    delete_document,
)
from perry.db.session import DatabaseSessionManager


document_router = APIRouter()


@document_router.get("/{document_id}", response_model=APIDocument)
async def get_document_by_id(
    document_id: int, api_user: Annotated[str, Depends(get_current_user)]
):
    pass


@document_router.get("/", response_model=list[APIDocument])
async def get_all_documents(api_user: Annotated[str, Depends(get_current_user)]):
    pass


@document_router.post("/", response_model=APIDocument)
async def create_document(
    document: APIDocument,
    api_user: Annotated[str, Depends(get_current_user)],
):
    pass


@document_router.put("/{document_id}", response_model=APIDocument)
async def update_document(
    document_id: int,
    document: APIDocument,
    api_user: Annotated[str, Depends(get_current_user)],
):
    pass


@document_router.delete("/{document_id}")
async def delete_document(
    document_id: int, api_user: Annotated[str, Depends(get_current_user)]
):
    pass
