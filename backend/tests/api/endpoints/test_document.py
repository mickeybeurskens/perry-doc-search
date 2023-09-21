from perry.api.endpoints.document import *
from fastapi import status
from tests.conftest import get_mock_secret_key
from tests.api.fixtures import *
from unittest.mock import patch


def get_document_url():
    return "/documents"


def mock_get_user_id(test_client, user_id):
    test_client.app.dependency_overrides[get_current_user_id] = lambda: user_id


def mock_api_doc(*args, **kwargs):
    return APIDocument(title="Test Document", id=1)


@pytest.fixture(scope="function")
def mock_get_document(monkeypatch):
    monkeypatch.setattr("perry.api.endpoints.document.get_document", mock_api_doc)


@pytest.fixture(scope="function")
def mock_document_owned_by_user(monkeypatch):
    monkeypatch.setattr(
        "perry.api.endpoints.document.document_owned_by_user",
        lambda *args, **kwargs: True,
    )


@pytest.mark.parametrize(
    "endpoint, method, status_code",
    [
        (get_document_url(), "GET", status.HTTP_401_UNAUTHORIZED),
        (get_document_url(), "POST", status.HTTP_401_UNAUTHORIZED),
        (get_document_url() + "/1", "GET", status.HTTP_401_UNAUTHORIZED),
        (get_document_url() + "/1", "PUT", status.HTTP_401_UNAUTHORIZED),
        (get_document_url() + "/1", "DELETE", status.HTTP_401_UNAUTHORIZED),
    ],
)
def test_endpoints_should_refuse_non_authenticated_users_available(
    test_client, endpoint, method, status_code
):
    response = test_client.request(method, endpoint)
    assert response.status_code == status_code


def test_should_return_document_when_authorized(
    test_client, mock_document_owned_by_user, mock_get_document
):
    mock_get_user_id(test_client, 1)
    response = test_client.get(get_document_url() + "/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == mock_api_doc().dict()


def test_should_raise_403_when_unauthorized(
    test_client, monkeypatch, mock_get_document
):
    mock_get_user_id(test_client, 1)
    monkeypatch.setattr(
        "perry.api.endpoints.document.document_owned_by_user",
        lambda *args, **kwargs: False,
    )
    response = test_client.get("/documents/1")
    assert response.status_code == status.HTTP_403_FORBIDDEN
