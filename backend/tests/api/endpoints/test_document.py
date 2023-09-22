from unittest.mock import Mock
from perry.api.endpoints.document import *
from tests.conftest import get_mock_secret_key
from tests.api.fixtures import *


def get_document_url():
    return "/documents/info"


def get_file_url():
    return "/documents/file"


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


@pytest.fixture(scope="function")
def mock_get_user_documents(monkeypatch):
    monkeypatch.setattr(
        "perry.api.endpoints.document.get_user_documents",
        lambda *args, **kwargs: [mock_api_doc()],
    )


@pytest.fixture(scope="function")
def mock_create_doc_db_operations(monkeypatch, test_client):
    mock_save_file = Mock(return_value=1)
    mock_update_document = Mock(side_effect=lambda db, doc_id, *args, **kwargs: doc_id)
    mock_remove_file = Mock(return_value=None)

    monkeypatch.setattr("perry.api.endpoints.document.save_file", mock_save_file)
    monkeypatch.setattr(
        "perry.api.endpoints.document.update_document", mock_update_document
    )
    monkeypatch.setattr("perry.api.endpoints.document.remove_file", mock_remove_file)
    user_id = 1
    mock_get_user_id(test_client, user_id)
    file_content = b"Some PDF content"

    return mock_save_file, mock_update_document, mock_remove_file, file_content, user_id


@pytest.mark.parametrize(
    "endpoint, method, status_code",
    [
        (get_file_url() + "/1", "GET", status.HTTP_401_UNAUTHORIZED),
        (get_file_url() + "/", "POST", status.HTTP_401_UNAUTHORIZED),
        (get_file_url() + "/1", "PUT", status.HTTP_401_UNAUTHORIZED),
        (get_file_url() + "/1", "DELETE", status.HTTP_401_UNAUTHORIZED),
        (get_document_url() + "/", "GET", status.HTTP_401_UNAUTHORIZED),
        (get_document_url() + "/1", "GET", status.HTTP_401_UNAUTHORIZED),
    ],
)
def test_endpoints_should_refuse_non_authenticated_users_available(
    test_client, endpoint, method, status_code
):
    response = test_client.request(method, endpoint)
    assert response.status_code == status_code


def test_create_doc_valid_pdf(test_client, mock_create_doc_db_operations):
    (
        save_file,
        update_document,
        remove_file,
        file_content,
        _,
    ) = mock_create_doc_db_operations
    file_name = "filename.pdf"

    response = test_client.post(
        get_file_url() + "/",
        files={"file": (file_name, file_content, "application/pdf")},
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {"id": 1}
    assert save_file.call_count == 1
    assert update_document.call_count == 1
    assert update_document.call_args[1]["title"] == file_name
    assert update_document.call_args[1]["user_ids"] == [1]
    assert remove_file.call_count == 0


def test_create_doc_invalid_file_type(test_client, mock_create_doc_db_operations):
    (
        save_file,
        update_document,
        remove_file,
        file_content,
        _,
    ) = mock_create_doc_db_operations

    response = test_client.post(
        get_file_url() + "/",
        files={"file": ("filename.txt", file_content, "application/txt")},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert save_file.call_count == 0
    assert update_document.call_count == 0
    assert remove_file.call_count == 0


def test_create_doc_server_error(
    test_client, monkeypatch, mock_create_doc_db_operations
):
    _, update_document, remove_file, file_content, _ = mock_create_doc_db_operations

    def mock_save_file(*args, **kwargs):
        raise Exception("Server Error")

    monkeypatch.setattr("perry.api.endpoints.document.save_file", mock_save_file)
    response = test_client.post(
        get_file_url() + "/",
        files={"file": ("filename.pdf", file_content, "application/pdf")},
    )

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert update_document.call_count == 0
    assert remove_file.call_count == 0


def test_create_doc_update_error_should_remove_file(
    test_client, monkeypatch, mock_create_doc_db_operations
):
    save_file, _, remove_file, file_content, _ = mock_create_doc_db_operations

    def mock_update_file(*args, **kwargs):
        raise Exception("Server Error")

    monkeypatch.setattr(
        "perry.api.endpoints.document.update_document", mock_update_file
    )
    response = test_client.post(
        get_file_url() + "/",
        files={"file": ("filename.pdf", file_content, "application/pdf")},
    )

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert save_file.call_count == 1
    assert remove_file.call_count == 1


@pytest.mark.parametrize(
    "ownership, remove_success, expected_status",
    [
        (True, True, status.HTTP_200_OK),
        (True, False, status.HTTP_500_INTERNAL_SERVER_ERROR),
        (False, True, status.HTTP_403_FORBIDDEN),
    ],
)
def test_delete_file(
    test_client, monkeypatch, ownership, remove_success, expected_status
):
    monkeypatch.setattr(
        "perry.api.endpoints.document.document_owned_by_user",
        lambda *args, **kwargs: ownership,
    )

    if remove_success:
        mock_remove_file = Mock(return_value=None)
    else:
        mock_remove_file = Mock(side_effect=Exception("Could not delete"))
    monkeypatch.setattr("perry.api.endpoints.document.remove_file", mock_remove_file)

    mock_get_user_id(test_client, 1)
    response = test_client.delete(get_file_url() + "/1")

    assert response.status_code == expected_status

    if ownership:
        assert mock_remove_file.called

    if not ownership:
        assert not mock_remove_file.called


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
    response = test_client.get(get_document_url() + "/1")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_doc_raises_404_when_doc_not_found(
    test_client, monkeypatch, mock_document_owned_by_user
):
    mock_get_user_id(test_client, 1)
    monkeypatch.setattr(
        "perry.api.endpoints.document.get_document",
        lambda *args, **kwargs: None,
    )
    response = test_client.get(get_document_url() + "/1")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_all_doc_info_returns_all_user_documents(
    test_client, mock_get_user_documents
):
    mock_get_user_id(test_client, 1)
    response = test_client.get(get_document_url() + "/")
    assert response.status_code == status.HTTP_200_OK
