from typing import Annotated
from pydantic import BaseModel
from fastapi import APIRouter, Depends
from perry.api.authentication import get_current_user_id
from perry.agents.base import AgentRegistry


agent_router = APIRouter()


class AgentInfo(BaseModel):
    name: str
    settings_schema: dict


@agent_router.get("/info", response_model=list[AgentInfo])
async def get_agent_registry_info(
    db_user_id: Annotated[int, Depends(get_current_user_id)],
):
    agent_types = AgentRegistry().get_agent_types()
    info = []
    if agent_types:
        for agent_type in agent_types:
            info.append(
                AgentInfo(
                    name=agent_type,
                    settings_schema=AgentRegistry().get_agent_settings_schema(
                        agent_type
                    ),
                )
            )
    return info
