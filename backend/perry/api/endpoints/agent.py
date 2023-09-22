from typing import Annotated
from fastapi import APIRouter, Depends, status, HTTPException
from perry.api.authentication import get_current_user_id
from perry.api.schemas import APIDocument
from perry.db.operations.agents import (
    create_agent,
    delete_agent,
    read_agent,
    update_agent,
)
from perry.db.session import DatabaseSessionManager as DSM


agent_router = APIRouter()
