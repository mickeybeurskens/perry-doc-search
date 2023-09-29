import pytest
from unittest.mock import Mock
from tests.api.fixtures import test_client, mock_get_user_id
from perry.api.app import AGENTS_URL
from perry.agents.base import AgentRegistry
from tests.agents.fixtures import DummyAgent


@pytest.fixture
def mock_agent_registry(monkeypatch):
    monkeypatch.setattr(
        "perry.api.app.init_agent_registry", Mock(return_value=AgentRegistry())
    )
    registry = AgentRegistry()
    registry.register_agent(DummyAgent)
    yield registry
    registry._instance = None


@pytest.mark.parametrize(
    "endpoint, method, status_code",
    [
        (AGENTS_URL + "/info", "GET", 401),
    ],
)
def test_endpoint_returns_401_if_not_logged_in(
    test_client, endpoint, method, status_code
):
    response = test_client.get(AGENTS_URL + "/info")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_get_agent_registry_info_returns_agent_schemas(
    test_client, mock_get_user_id, mock_agent_registry
):
    # TODO: Isolate agent registry for testing so it does not load all agents
    response = test_client.get(AGENTS_URL + "/info")
    assert response.status_code == 200
    assert {
        "name": DummyAgent.__name__,
        "settings_schema": DummyAgent._get_config_class().schema()["properties"],
    } in response.json()
