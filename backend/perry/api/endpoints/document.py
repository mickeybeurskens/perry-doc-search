from typing import Annotated
from fastapi import APIRouter, Depends, status, HTTPException
from perry.api.authentication import get_current_user_id
from perry.api.schemas import APIDocument, APIUser
from perry.db.operations.documents import (
    get_document,
    create_document,
    update_document,
    delete_document,
    document_owned_by_user,
)
from perry.db.session import DatabaseSessionManager as DSM


document_router = APIRouter()


@document_router.get("/{document_id}", response_model=APIDocument)
async def get_doc_by_id(
    document_id: int, db_user_id: Annotated[int, Depends(get_current_user_id)]
):
    doc = get_document(DSM.get_db_session, document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    if not document_owned_by_user(DSM.get_db_session, document_id, db_user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to get document",
        )
    return APIDocument(title=doc.title, id=doc.id)


@document_router.get("/", response_model=list[APIDocument])
async def get_all_docs(db_user_id: Annotated[int, Depends(get_current_user_id)]):
    pass


@document_router.post("/", response_model=APIDocument)
async def create_doc(
    document: APIDocument,
    db_user_id: Annotated[int, Depends(get_current_user_id)],
):
    pass


@document_router.put("/{document_id}", response_model=APIDocument)
async def update_doc(
    document_id: int,
    document: APIDocument,
    db_user_id: Annotated[int, Depends(get_current_user_id)],
):
    pass


@document_router.delete("/{document_id}")
async def delete_doc(
    document_id: int, db_user_id: Annotated[int, Depends(get_current_user_id)]
):
    pass
