from typing import Annotated
from fastapi import APIRouter, Depends, status, HTTPException
from perry.api.authentication import get_current_user_id
from perry.api.schemas import APIDocument
from perry.db.operations.documents import (
    get_document,
    get_user_documents,
    update_document,
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
from perry.agents.manager import AgentManager
from perry.agents.base import AgentRegistry


conversation_router = APIRouter()


from pydantic import BaseModel


class ConversationConfig(BaseModel):
    name: str
    agent_type: str
    agent_settings: dict
    doc_ids: list[int]


@conversation_router.post("/", status_code=status.HTTP_201_CREATED)
async def conversation_agent_setup(
    conversation_config: ConversationConfig,
    db_user_id: Annotated[int, Depends(get_current_user_id)],
):
    db = DSM.get_db_session
    # check doc ids
    docs = get_user_documents(db, db_user_id)
    user_document_ids = [doc.id for doc in docs]
    if not set(conversation_config.doc_ids).issubset(set(user_document_ids)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid document ids provided.",
        )

    # create agent
    # check type in the agent and return a class instance
    try:
        agent_class = AgentRegistry.get_agent_class(conversation_config.agent_type)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid agent type provided.",
        )

    try:
        agent = agent_class(db, conversation_config.agent_settings)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid agent settings provided.",
        )

    conversation_id = create_conversation()
    try:
        update_conversation(db, conversation_id, user_id=db_user_id)
        update_agent(db, agent, conversation_id=conversation_id)
        for doc in docs:
            conv_ids = [conv.id for conv in doc.conversations]
            update_document(db, doc.id, conversation_id=conv_ids + [conversation_id])
    except Exception:
        remove_conversation(db, conversation_id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create conversation.",
        )
    return conversation_id


@conversation_router.get("/{conversation_id}", status_code=status.HTTP_200_OK)
async def get_conversation_info(
    conversation_id: int, db_user_id: Annotated[int, Depends(get_current_user_id)]
):
    pass


@conversation_router.delete("/{conversation_id}", status_code=status.HTTP_200_OK)
async def remove_conversation(
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
