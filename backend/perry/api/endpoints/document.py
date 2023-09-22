from typing import Annotated
from fastapi import APIRouter, Depends, status, HTTPException, UploadFile
from perry.api.authentication import get_current_user_id
from perry.api.schemas import APIDocument
from perry.db.operations.documents import (
    save_file,
    remove_file,
    load_file,
    get_document,
    update_document,
    document_owned_by_user,
    get_user_documents,
)
from perry.db.session import DatabaseSessionManager as DSM


file_router = APIRouter()
document_router = APIRouter()


@file_router.post("/", status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile,
    db_user_id: Annotated[int, Depends(get_current_user_id)],
):
    if not file.content_type == "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a PDF",
        )
    try:
        doc_id = save_file(DSM.get_db_session, file, ".pdf")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not save file",
        )
    try:
        update_document(
            DSM.get_db_session, doc_id, title=file.filename, user_ids=[db_user_id]
        )
    except Exception as e:
        remove_file(DSM.get_db_session, doc_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not update document",
        )
    return {"id": doc_id}


@file_router.delete("/{document_id}", status_code=status.HTTP_200_OK)
async def delete_file(
    document_id: int, db_user_id: Annotated[int, Depends(get_current_user_id)]
):
    if not document_owned_by_user(DSM.get_db_session, document_id, db_user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete document",
        )
    try:
        remove_file(DSM.get_db_session, document_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not delete file",
        )


@file_router.get("/{document_id}", response_model=UploadFile)
async def retrieve_file_binary(
    document_id: int,
    db_user_id: Annotated[int, Depends(get_current_user_id)],
):
    if not document_owned_by_user(DSM.get_db_session, document_id, db_user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to get document",
        )
    try:
        file_bytes = load_file(DSM.get_db_session, document_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not load file",
        )
    return UploadFile(file=file_bytes, filename="filename.pdf")


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
    db_documents = get_user_documents(DSM.get_db_session, db_user_id)
    docs = []
    for doc in db_documents:
        docs.append(APIDocument(title=doc.title, id=doc.id))
    return docs
