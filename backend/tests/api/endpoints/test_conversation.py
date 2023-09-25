import pytest
from unittest.mock import Mock
from fastapi import status
from perry.api.app import CONVERSATION_URL
from perry.api.endpoints.conversation import get_current_user_id, ConversationConfig
from tests.api.fixtures import *


def get_test_user_id():
    return 1


def get_fake_auth_header():
    return {"Authorization": f"Bearer {mocked_valid_token()}"}


def get_create_conversation_json():
    return ConversationConfig(
        name="test_conversation",
        agent_type="dummy",
        agent_settings={},
        doc_ids=[1, 2, 3],
    ).dict()


def str_path_conv_endpoint() -> str:
    return "perry.api.endpoints.conversation"


@pytest.fixture(scope="function")
def create_conversation_mock(test_client, monkeypatch):
    test_client.app.dependency_overrides[
        get_current_user_id
    ] = lambda: get_test_user_id()
    monkeypatch.setattr(str_path_conv_endpoint() + ".create_conversation", lambda: True)
    mock_get_user_documents = Mock(
        return_value=[
            Mock(id=1, conversations=[]),
            Mock(id=2, conversations=[]),
            Mock(id=3, conversations=[]),
        ]
    )
    monkeypatch.setattr(
        str_path_conv_endpoint() + ".get_user_documents", mock_get_user_documents
    )
    mock_agent = Mock()
    mock_agent_constructor = Mock(return_value=mock_agent)
    monkeypatch.setattr(
        str_path_conv_endpoint() + ".AgentRegistry.get_agent_class",
        mock_agent_constructor,
    )

    conversation_json = get_create_conversation_json()
    conversation_json["agent_settings"] = {"invalid_agent_settings": True}

    mock_update_conversation = Mock(return_value=True)
    monkeypatch.setattr(
        str_path_conv_endpoint() + ".update_conversation", mock_update_conversation
    )
    mock_update_agent = Mock(return_value=True)
    monkeypatch.setattr(str_path_conv_endpoint() + ".update_agent", mock_update_agent)
    mock_update_document = Mock(return_value=True)
    monkeypatch.setattr(
        str_path_conv_endpoint() + ".update_document", mock_update_document
    )

    yield {
        "test_client": test_client,
        "mock_agent": mock_agent,
        "mock_agent_constructor": mock_agent_constructor,
        "mock_get_user_documents": mock_get_user_documents,
        "conversation_json": conversation_json,
        "mock_update_conversation": mock_update_conversation,
        "mock_update_agent": mock_update_agent,
        "mock_update_document": mock_update_document,
    }


@pytest.mark.parametrize(
    "endpoint, method, status_code",
    [
        (CONVERSATION_URL + "/", "POST", status.HTTP_401_UNAUTHORIZED),
        (CONVERSATION_URL + "/1", "POST", status.HTTP_401_UNAUTHORIZED),
        (CONVERSATION_URL + "/1", "GET", status.HTTP_401_UNAUTHORIZED),
        (CONVERSATION_URL + "/1", "DELETE", status.HTTP_401_UNAUTHORIZED),
    ],
)
def test_endpoints_should_refuse_non_authenticated_users(
    test_client, endpoint, method, status_code
):
    response = test_client.request(method, endpoint)
    assert response.status_code == status_code


def test_create_conversation_errors_with_unowned_doc_ids(create_conversation_mock):
    test_client = create_conversation_mock["test_client"]
    mock_get_user_documents = create_conversation_mock["mock_get_user_documents"]
    invalid_doc_ids = [-1]

    conversation_json = get_create_conversation_json()
    conversation_json["doc_ids"] = invalid_doc_ids

    response = test_client.post(
        CONVERSATION_URL + "/",
        json=conversation_json,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Invalid document ids provided."}
    assert mock_get_user_documents.call_count == 1


def test_create_conversation_errors_with_invalid_agent_type(create_conversation_mock):
    test_client = create_conversation_mock["test_client"]
    mock_get_user_documents = create_conversation_mock["mock_get_user_documents"]
    mock_agent_constructor = create_conversation_mock["mock_agent_constructor"]
    conversation_json = create_conversation_mock["conversation_json"]

    conversation_json["agent_type"] = "invalid_agent_type"
    mock_agent_constructor.side_effect = KeyError("Invalid agent type")

    response = test_client.post(
        CONVERSATION_URL + "/",
        json=conversation_json,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Invalid agent type provided."}
    assert mock_get_user_documents.call_count == 1


def test_create_conversation_errors_with_invalid_agent_settings(
    create_conversation_mock,
):
    test_client = create_conversation_mock["test_client"]
    mock_get_user_documents = create_conversation_mock["mock_get_user_documents"]
    conversation_json = create_conversation_mock["conversation_json"]
    mock_agent = create_conversation_mock["mock_agent"]

    mock_agent.side_effect = KeyError("Invalid agent settings")
    conversation_json["agent_settings"] = {"invalid_agent_settings": True}

    response = test_client.post(
        CONVERSATION_URL + "/",
        json=conversation_json,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Invalid agent settings provided."}
    assert mock_get_user_documents.call_count == 1


@pytest.mark.parametrize(
    "method, exception",
    [
        ("update_conversation", KeyError("Invalid conversation")),
        ("update_agent", KeyError("Invalid agent")),
        ("update_document", KeyError("Invalid document")),
    ],
)
def test_create_conversation_errors_on_db_exceptions(
    create_conversation_mock, method, exception, monkeypatch
):
    test_client = create_conversation_mock["test_client"]

    monkeypatch.setattr(
        str_path_conv_endpoint() + f".{method}", Mock(side_effect=exception)
    )

    response = test_client.post(
        CONVERSATION_URL + "/",
        json=create_conversation_mock["conversation_json"],
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Could not create conversation."}


def test_create_conversation_succeeds(create_conversation_mock):
    response = create_conversation_mock["test_client"].post(
        CONVERSATION_URL + "/",
        json=create_conversation_mock["conversation_json"],
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert create_conversation_mock["mock_get_user_documents"].call_count == 1
    assert create_conversation_mock["mock_agent_constructor"].call_count == 1
    assert create_conversation_mock["mock_agent"].call_count == 1
    assert create_conversation_mock["mock_update_conversation"].call_count == 1
    assert create_conversation_mock["mock_update_agent"].call_count == 1
    assert create_conversation_mock["mock_update_document"].call_count == 3


def test_create_conversation_updates_document_with_conversation_id(
    create_conversation_mock,
):
    test_client = create_conversation_mock["test_client"]
    mock_update_document = create_conversation_mock["mock_update_document"]
    mock_update_document.side_effect = lambda db, doc_id, **kwargs: doc_id

    response = test_client.post(
        CONVERSATION_URL + "/",
        json=create_conversation_mock["conversation_json"],
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert mock_update_document.call_count == 3
    assert mock_update_document.call_args_list[0][1]["conversation_id"] == [1]
    assert mock_update_document.call_args_list[1][1]["conversation_id"] == [1]
    assert mock_update_document.call_args_list[2][1]["conversation_id"] == [1]
