from typing import Annotated
from fastapi import APIRouter, Depends, status, HTTPException, UploadFile
from sqlalchemy.orm import Session
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
from perry.db.operations.users import get_user, User as DBUser
from perry.api.dependencies import get_db


file_router = APIRouter()
document_router = APIRouter()


def check_file_type(file_type: str):
    if not file_type == "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a PDF",
        )


def check_file_size(file_size: int):
    file_size_limit = 10e6
    if file_size > file_size_limit:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File must be smaller than {file_size_limit/1e6}MB",
        )


def check_max_documents(user: DBUser):
    doc_limit = 20
    if len(user.documents) > doc_limit:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User cannot have more than {doc_limit} documents",
        )


def api_doc_from_db_doc(db_doc):
    return APIDocument(title=db_doc.title, id=db_doc.id, description=db_doc.description)


@file_router.post("/", status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile,
    db_user_id: Annotated[int, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
):
    check_file_type(file.content_type)
    check_file_size(file.size)
    check_max_documents(get_user(db, db_user_id))

    try:
        doc_id = save_file(db, file.file, "pdf")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not save file",
        )
    try:
        update_document(db, doc_id, title=file.filename, user_ids=[db_user_id])
    except Exception as e:
        remove_file(db, doc_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not update document",
        )
    return {"id": doc_id}


@file_router.delete("/{document_id}", status_code=status.HTTP_200_OK)
async def delete_file(
    document_id: int,
    db_user_id: Annotated[int, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
):
    if not document_owned_by_user(db, document_id, db_user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete document",
        )
    try:
        remove_file(db, document_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not delete file",
        )


@file_router.get("/{document_id}", response_model=UploadFile)
async def retrieve_file_binary(
    document_id: int,
    db_user_id: Annotated[int, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
):
    db_doc = get_document(db, document_id)
    if not db_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    if not document_owned_by_user(db, document_id, db_user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to get document",
        )
    try:
        file_bytes = load_file(db, document_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not load file",
        )
    return UploadFile(file=file_bytes, filename=db_doc.title)


@document_router.get("/", response_model=list[APIDocument])
async def get_all_docs(
    db_user_id: Annotated[int, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
):
    db_documents = get_user_documents(db, db_user_id)
    docs = []
    for doc in db_documents:
        docs.append(
            api_doc_from_db_doc(doc),
        )
    return docs


@document_router.get("/{document_id}", response_model=APIDocument)
async def get_doc_by_id(
    document_id: int,
    db_user_id: Annotated[int, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
):
    doc = get_document(db, document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    if not document_owned_by_user(db, document_id, db_user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to get document",
        )
    return api_doc_from_db_doc(doc)


@document_router.put("/{document_id}", status_code=status.HTTP_200_OK)
async def update_doc_description(
    document_id: int,
    info: APIDocument,
    db_user_id: Annotated[int, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
):
    if not document_owned_by_user(db, document_id, db_user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update document",
        )
    try:
        update_document(db, document_id, description=info.description)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not update document",
        )
