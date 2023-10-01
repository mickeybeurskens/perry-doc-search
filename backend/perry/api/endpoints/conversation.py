from typing import Annotated
from datetime import datetime
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from perry.api.authentication import get_current_user_id
from perry.api.schemas import APIDocument
from perry.db.operations.documents import (
    get_user_documents,
    update_document,
)
from perry.db.operations.conversations import (
    create_conversation,
    delete_conversation,
    read_conversation,
    update_conversation,
    add_messages_to_conversation,
    Conversation as DBConversation,
)
from perry.db.operations.messages import create_message, delete_message
from perry.db.operations.agents import update_agent, create_agent
from perry.db.operations.users import get_user
from perry.agents.manager import AgentManager
from perry.agents.base import AgentRegistry
from perry.api.dependencies import get_db


conversation_router = APIRouter()


from pydantic import BaseModel


class ConversationMessage(BaseModel):
    role: str
    message: str
    timestamp: datetime


class ConversationConfig(BaseModel):
    name: str
    agent_type: str
    agent_settings: dict
    doc_ids: list[int]


class ConversationQuery(BaseModel):
    query: str


class ConversationInfo(BaseModel):
    id: int
    name: str
    user_id: int
    agent_type: str
    agent_settings: dict
    doc_ids: list[int]
    doc_titles: list[str]


def check_owned_conversation(db, conversation_id, user_id) -> DBConversation:
    conversation = read_conversation(db, conversation_id)
    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Conversation not found.",
        )
    if conversation.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Conversation not authorized.",
        )


def conversation_db_to_info(db_conversation: DBConversation) -> ConversationInfo:
    return ConversationInfo(
        id=db_conversation.id,
        name=db_conversation.name,
        user_id=db_conversation.user_id,
        agent_type=db_conversation.agent.type,
        agent_settings=db_conversation.agent.config,
        doc_ids=[doc.id for doc in db_conversation.documents],
        doc_titles=[doc.title for doc in db_conversation.documents],
    )


@conversation_router.get(
    "/", status_code=status.HTTP_200_OK, response_model=list[ConversationInfo]
)
async def get_user_conversations(
    db_user_id: Annotated[int, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
):
    conversations = get_user(db, db_user_id).conversations
    return [conversation_db_to_info(conv) for conv in conversations]


@conversation_router.post("/", status_code=status.HTTP_201_CREATED)
async def conversation_agent_setup(
    conversation_config: ConversationConfig,
    db_user_id: Annotated[int, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
):
    docs = get_user_documents(db, db_user_id)
    user_document_ids = [doc.id for doc in docs]
    if not set(conversation_config.doc_ids).issubset(set(user_document_ids)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid document ids provided.",
        )

    try:
        agent_class = AgentRegistry().get_agent_class(conversation_config.agent_type)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid agent type provided.",
        )
    new_agent_id = create_agent(db)

    conversation_id = create_conversation(db)
    try:
        update_conversation(
            db,
            conversation_id,
            user_id=db_user_id,
            name=conversation_config.name,
        )
        update_agent(db, new_agent_id, conversation_id=conversation_id)
        for doc in docs:
            conv_ids = [conv.id for conv in doc.conversations]
            update_document(db, doc.id, conversation_ids=conv_ids + [conversation_id])
    except Exception:
        delete_conversation(db, conversation_id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create conversation.",
        )

    try:
        agent = agent_class(
            db, conversation_config.agent_settings, agent_id=new_agent_id
        )
        agent.save()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Agent could not be created.",
        )
    return conversation_id


@conversation_router.get("/{conversation_id}", status_code=status.HTTP_200_OK)
async def get_conversation_info(
    conversation_id: int,
    db_user_id: Annotated[int, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
):
    check_owned_conversation(db, conversation_id, db_user_id)
    conversation = read_conversation(db, conversation_id)
    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Conversation not found.",
        )
    return conversation_db_to_info(conversation)


@conversation_router.get("/{conversation_id}/messages", status_code=status.HTTP_200_OK)
async def get_conversation_message_history(
    conversation_id: int,
    db_user_id: Annotated[int, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
):
    check_owned_conversation(db, conversation_id, db_user_id)
    conversation = read_conversation(db, conversation_id)
    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Conversation not found.",
        )
    return [
        ConversationMessage(
            role=message.role, message=message.message, timestamp=message.timestamp
        )
        for message in conversation.messages
    ]


@conversation_router.delete("/{conversation_id}", status_code=status.HTTP_200_OK)
async def remove_conversation_history(
    conversation_id: int,
    db_user_id: Annotated[int, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
):
    check_owned_conversation(db, conversation_id, db_user_id)
    delete_conversation(db, conversation_id)


@conversation_router.post("/{conversation_id}", status_code=status.HTTP_200_OK)
async def query_conversation_agent(
    conversation_query: ConversationQuery,
    conversation_id: int,
    db_user_id: Annotated[int, Depends(get_current_user_id)],
    db: Session = Depends(get_db),
):
    agent_manager = AgentManager()
    check_owned_conversation(db, conversation_id, db_user_id)

    agent_not_found_exception = HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Could not load agent.",
    )
    try:
        conversation = read_conversation(db, conversation_id)
        agent = agent_manager.load_agent(db, conversation.agent.id)
        if not agent:
            raise agent_not_found_exception
    except Exception:
        raise agent_not_found_exception

    query_failed_exception = HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Query failed.",
    )

    try:
        answer = await agent.query(conversation_query.query)
    except Exception:
        raise query_failed_exception

    user_message_id = create_message(db, db_user_id, "user", conversation_query.query)
    agent_message_id = create_message(db, db_user_id, "assistant", answer)
    if not add_messages_to_conversation(
        db, conversation_id, [user_message_id, agent_message_id]
    ):
        delete_message(db, user_message_id)
        delete_message(db, agent_message_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not add messages to conversation.",
        )
    return answer
