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
def create_conversation_test_client(test_client, monkeypatch):
    test_client.app.dependency_overrides[
        get_current_user_id
    ] = lambda: get_test_user_id()
    monkeypatch.setattr(str_path_conv_endpoint() + ".create_conversation", lambda: True)
    yield test_client


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


def test_create_conversation_errors_with_unowned_doc_ids(
    create_conversation_test_client, monkeypatch
):
    valid_doc_ids = [1, 2, 3]
    invalid_doc_ids = valid_doc_ids + [4]
    mock_get_user_documents = Mock(
        return_value=[Mock(id=doc_id) for doc_id in valid_doc_ids]
    )
    monkeypatch.setattr(
        str_path_conv_endpoint() + ".get_user_documents", mock_get_user_documents
    )

    conversation_json = get_create_conversation_json()
    conversation_json["doc_ids"] = invalid_doc_ids

    response = create_conversation_test_client.post(
        CONVERSATION_URL + "/",
        json=conversation_json,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Invalid document ids provided."}
    assert mock_get_user_documents.call_count == 1
