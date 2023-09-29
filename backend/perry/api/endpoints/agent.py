from typing import Annotated
from pydantic import BaseModel
from fastapi import APIRouter, Depends
from perry.api.authentication import get_current_user_id
from perry.agents.subquestion import SubquestionAgent
from perry.agents.base import AgentRegistry
from perry.agents.echo import EchoAgent


def init_registry() -> AgentRegistry:
    registry = AgentRegistry()
    registry.register_agent("Echo", EchoAgent)
    registry.register_agent("Subquestion", SubquestionAgent)
    return registry


AGENT_REGISTRY = init_registry()


agent_router = APIRouter()


class AgentInfo(BaseModel):
    name: str
    settings_schema: dict


@agent_router.get("/info", response_model=list[AgentInfo])
async def get_agent_registry_info(
    db_user_id: Annotated[int, Depends(get_current_user_id)],
):
    agent_types = AGENT_REGISTRY.get_agent_types()
    info = []
    if agent_types:
        for agent_type in agent_types:
            info.append(
                AgentInfo(
                    name=agent_type,
                    settings_schema=AGENT_REGISTRY.get_agent_settings_schema(
                        agent_type
                    ),
                )
            )
    return info
