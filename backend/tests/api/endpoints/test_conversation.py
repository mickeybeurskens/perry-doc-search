import pytest
from unittest.mock import Mock, AsyncMock
from fastapi import status
from perry.api.app import CONVERSATION_URL
from perry.api.endpoints.conversation import (
    get_current_user_id,
    ConversationConfig,
    ConversationQuery,
    check_owned_conversation,
)
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


def get_mock_conversation(id=1, user_id=1):
    return Mock(
        id=id,
        user_id=user_id,
        agent=Mock(config={}),
        documents=[
            Mock(id=1, title=""),
            Mock(id=2, title=""),
            Mock(id=3, title=""),
        ],
    )


@pytest.fixture(scope="function")
def conversation_mock(mock_get_user_id):
    yield


@pytest.fixture(scope="function")
def check_owned_mock(monkeypatch):
    monkeypatch.setattr(
        str_path_conv_endpoint() + ".check_owned_conversation",
        lambda db, conv_id, user_id: True,
    )
    yield


@pytest.fixture(scope="function")
def get_user_conversation_mock(conversation_mock, test_client, monkeypatch):
    conversations = [
        get_mock_conversation(1, 1),
        get_mock_conversation(2, 2),
        get_mock_conversation(3, 3),
    ]
    user = Mock(conversations=conversations)
    monkeypatch.setattr(str_path_conv_endpoint() + ".get_user", lambda db, id: user)
    yield {
        "test_client": test_client,
        "conversations": conversations,
    }


@pytest.fixture(scope="function")
def create_conversation_mock(conversation_mock, test_client, monkeypatch):
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


@pytest.fixture(scope="function")
def query_conversation_agent_mock(conversation_mock, test_client, monkeypatch):
    conversation = Mock(user_id=get_test_user_id())
    monkeypatch.setattr(
        str_path_conv_endpoint() + ".read_conversation", lambda db, id: conversation
    )

    response = "test_response"
    agent = AsyncMock()
    agent.query.return_value = response
    monkeypatch.setattr(
        str_path_conv_endpoint() + ".AgentManager.load_agent",
        lambda self, db, id: agent,
    )
    query = ConversationQuery(query="test_query").dict()
    yield {
        "test_client": test_client,
        "conversation": conversation,
        "agent": agent,
        "query": query,
        "response": response,
    }


@pytest.mark.parametrize(
    "endpoint, method, status_code",
    [
        (CONVERSATION_URL + "/", "GET", status.HTTP_401_UNAUTHORIZED),
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


def test_get_user_conversations_returns_empty_list_if_no_conversations(
    get_user_conversation_mock, test_client, monkeypatch
):
    conversations = []
    user = Mock(conversations=conversations)
    monkeypatch.setattr(str_path_conv_endpoint() + ".get_user", lambda db, id: user)
    response = test_client.get(CONVERSATION_URL + "/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_get_user_conversations_returns_list_of_conversations(
    get_user_conversation_mock, test_client
):
    conversations = get_user_conversation_mock["conversations"]
    conversation_info_check = lambda conv: {
        "id": conv.id,
        "user_id": conv.user_id,
        "agent_settings": conv.agent.config,
        "doc_ids": [doc.id for doc in conv.documents],
        "doc_titles": [doc.title for doc in conv.documents],
    }
    return_json = [conversation_info_check(conv) for conv in conversations]
    response = test_client.get(CONVERSATION_URL + "/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == return_json


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


def test_query_conversation_agent_errors_on_non_authorized_conversation(
    query_conversation_agent_mock,
):
    test_client = query_conversation_agent_mock["test_client"]
    conversation = query_conversation_agent_mock["conversation"]
    conversation.user_id = -1

    response = test_client.post(
        CONVERSATION_URL + "/1",
        json=query_conversation_agent_mock["query"],
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Conversation not authorized."}


def test_query_conversation_agent_errors_on_invalid_conversation(
    query_conversation_agent_mock, monkeypatch
):
    test_client = query_conversation_agent_mock["test_client"]
    monkeypatch.setattr(
        str_path_conv_endpoint() + ".read_conversation", lambda db, id: None
    )

    response = test_client.post(
        CONVERSATION_URL + "/1",
        json=query_conversation_agent_mock["query"],
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Conversation not found."}


def test_query_conversation_agent_errors_on_invalid_agent(
    query_conversation_agent_mock, monkeypatch
):
    test_client = query_conversation_agent_mock["test_client"]
    monkeypatch.setattr(
        str_path_conv_endpoint() + ".AgentManager.load_agent", lambda self, db, id: None
    )

    response = test_client.post(
        CONVERSATION_URL + "/1",
        json=query_conversation_agent_mock["query"],
    )
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json() == {"detail": "Could not load agent."}


def test_query_conversation_agent_query_failure_raises_server_error(
    query_conversation_agent_mock,
):
    test_client = query_conversation_agent_mock["test_client"]
    agent = query_conversation_agent_mock["agent"]
    async_query = AsyncMock(side_effect=Exception("Query failed"))
    agent.query = async_query

    response = test_client.post(
        CONVERSATION_URL + "/1",
        json=query_conversation_agent_mock["query"],
    )
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json() == {"detail": "Query failed."}


def test_query_conversation_agent_succeeds(query_conversation_agent_mock):
    test_client = query_conversation_agent_mock["test_client"]
    agent = query_conversation_agent_mock["agent"]

    response = test_client.post(
        CONVERSATION_URL + "/1",
        json=query_conversation_agent_mock["query"],
    )
    assert response.status_code == status.HTTP_200_OK
    agent.called_once_with(query_conversation_agent_mock["query"]["query"])
    assert response.json() == query_conversation_agent_mock["response"]


def test_get_conversation_info_errors_on_non_authorized_conversation(
    conversation_mock, check_owned_mock, test_client, monkeypatch
):
    monkeypatch.setattr(
        str_path_conv_endpoint() + ".read_conversation", lambda db, id: None
    )

    response = test_client.get(CONVERSATION_URL + "/1")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Conversation not found."}


def test_get_conversation_info_succeeds(
    conversation_mock, check_owned_mock, test_client, monkeypatch
):
    moc_conversation = get_mock_conversation()
    monkeypatch.setattr(
        str_path_conv_endpoint() + ".read_conversation", lambda db, id: moc_conversation
    )

    response = test_client.get(CONVERSATION_URL + "/1")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": 1,
        "user_id": 1,
        "agent_settings": {},
        "doc_ids": [1, 2, 3],
        "doc_titles": ["", "", ""],
    }


def test_remove_conversation_history_calls_delete_conversation(
    conversation_mock, check_owned_mock, test_client, monkeypatch
):
    mock_delete_conversation = Mock(return_value=True)
    monkeypatch.setattr(
        str_path_conv_endpoint() + ".delete_conversation", mock_delete_conversation
    )

    response = test_client.delete(CONVERSATION_URL + "/1")

    assert response.status_code == status.HTTP_200_OK
    assert mock_delete_conversation.call_count == 1
    assert mock_delete_conversation.call_args_list[0][0][1] == 1


def test_check_owned_conversation_errors_on_not_found_conversation(monkeypatch):
    monkeypatch.setattr(
        str_path_conv_endpoint() + ".read_conversation", lambda db, id: None
    )
    with pytest.raises(Exception) as e:
        check_owned_conversation(Mock(), 1, 1)


def test_check_owned_conversation_errors_on_not_authorized(monkeypatch):
    monkeypatch.setattr(
        str_path_conv_endpoint() + ".read_conversation", lambda db, id: Mock(user_id=2)
    )
    with pytest.raises(Exception) as e:
        check_owned_conversation(Mock(), 1, 1)


def test_check_owned_conversation_succeeds(monkeypatch):
    monkeypatch.setattr(
        str_path_conv_endpoint() + ".read_conversation", lambda db, id: Mock(user_id=1)
    )
    check_owned_conversation(Mock(), 1, 1)
