from typing import Annotated
from fastapi import APIRouter, Depends, status, HTTPException
from perry.api.authentication import get_current_user_id
from perry.api.schemas import APIDocument
from perry.db.operations.documents import (
    get_document,
    get_user_documents,
)
from perry.db.operations.conversations import (
    create_conversation,
    delete_conversation,
    read_conversation,
    update_conversation,
)
from perry.db.operations.agents import (
    create_agent,
    delete_agent,
    read_agent,
    update_agent,
)
from perry.db.session import DatabaseSessionManager as DSM


conversation_router = APIRouter()


from pydantic import BaseModel


class ConversationConfig(BaseModel):
    name: str
    agent_type: str
    agent_settings: dict
    doc_ids: list[int]


@conversation_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_conversation(
    conversation_config: ConversationConfig,
    db_user_id: Annotated[int, Depends(get_current_user_id)],
):
    db = DSM.get_db_session
    # check doc ids
    user_document_ids = [doc.id for doc in get_user_documents(db, db_user_id)]
    if not set(conversation_config.doc_ids).issubset(set(user_document_ids)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid document ids provided.",
        )
    # create agent
    # create conversation
    # return conversation id


@conversation_router.get("/{conversation_id}", status_code=status.HTTP_200_OK)
async def get_conversation(
    conversation_id: int, db_user_id: Annotated[int, Depends(get_current_user_id)]
):
    pass


@conversation_router.delete("/{conversation_id}", status_code=status.HTTP_200_OK)
async def delete_conversation(
    conversation_id: int, db_user_id: Annotated[int, Depends(get_current_user_id)]
):
    pass


@conversation_router.post("/{conversation_id}", status_code=status.HTTP_200_OK)
async def query_conversation_agent(
    conversation_id: int,
    query: str,
    db_user_id: Annotated[int, Depends(get_current_user_id)],
):
    pass
