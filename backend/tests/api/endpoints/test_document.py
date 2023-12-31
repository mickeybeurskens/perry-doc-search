from io import BytesIO
from pathlib import Path
from unittest.mock import Mock
from perry.api.endpoints.document import *
from tests.conftest import get_mock_secret_key
from tests.api.fixtures import *
from perry.db.models import Document
from perry.api.app import DOCUMENTS_URL, FILES_URL


def get_document_url():
    return DOCUMENTS_URL


def get_file_url():
    return FILES_URL


def mock_api_doc(*args, **kwargs):
    return APIDocument(title="Test Document", id=1, description="test")


@pytest.fixture(scope="function")
def mock_get_user_id_and_return_id(test_client):
    user_id = 1
    test_client.app.dependency_overrides[get_current_user_id] = lambda: user_id
    yield user_id
    test_client.app.dependency_overrides.pop(get_current_user_id)


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
def mock_create_doc_db_operations(monkeypatch, test_client, mock_get_user_id):
    mock_save_file = Mock(return_value=1)
    mock_update_document = Mock(side_effect=lambda db, doc_id, *args, **kwargs: doc_id)
    mock_remove_file = Mock(return_value=None)

    monkeypatch.setattr("perry.api.endpoints.document.save_file", mock_save_file)
    monkeypatch.setattr(
        "perry.api.endpoints.document.update_document", mock_update_document
    )
    monkeypatch.setattr("perry.api.endpoints.document.remove_file", mock_remove_file)
    monkeypatch.setattr(
        "perry.api.endpoints.document.check_max_documents", lambda *args, **kwargs: None
    )
    user_id = mock_get_user_id_and_return_id
    file_content = b"Some PDF content"

    return mock_save_file, mock_update_document, mock_remove_file, file_content, user_id


@pytest.fixture(scope="function")
def mock_retrieve_binary_file_setup(monkeypatch, mock_get_user_id):
    document_id = 1

    mock_document_owned_by_user = Mock(return_value=True)
    monkeypatch.setattr(
        "perry.api.endpoints.document.document_owned_by_user",
        mock_document_owned_by_user,
    )
    db_doc_mock = Mock(spec=Document)
    db_doc_mock.title = "filename.pdf"
    mock_get_document = Mock(return_value=db_doc_mock)
    monkeypatch.setattr(
        "perry.api.endpoints.document.get_document",
        mock_get_document,
    )
    return document_id, mock_document_owned_by_user, mock_get_document


@pytest.mark.parametrize(
    "endpoint, method, status_code",
    [
        (get_file_url() + "/1", "GET", status.HTTP_401_UNAUTHORIZED),
        (get_file_url() + "/", "POST", status.HTTP_401_UNAUTHORIZED),
        (get_file_url() + "/1", "DELETE", status.HTTP_401_UNAUTHORIZED),
        (get_document_url() + "/", "GET", status.HTTP_401_UNAUTHORIZED),
        (get_document_url() + "/1", "GET", status.HTTP_401_UNAUTHORIZED),
        (get_document_url() + "/1", "PUT", status.HTTP_401_UNAUTHORIZED),
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


def test_upload_file_should_call_save_file_with_binaryio_object(
    test_client, monkeypatch, tmpdir, mock_get_user_id
):
    file_name = "filename.pdf"

    monkeypatch.setattr(
        "perry.db.operations.documents.get_file_storage_path",
        lambda *args, **kwargs: tmpdir,
    )
    monkeypatch.setattr(
        "perry.api.endpoints.document.update_document", lambda *args, **kwargs: True
    )
    monkeypatch.setattr(
        "perry.api.endpoints.document.check_max_documents", lambda *args, **kwargs: None
    )

    response = test_client.post(
        get_file_url() + "/",
        files={"file": (file_name, b"test_bin", "application/pdf")},
    )

    created_file_path = Path(tmpdir, "1.pdf")
    assert response.status_code == status.HTTP_201_CREATED
    assert created_file_path.exists()


@pytest.mark.parametrize(
    "ownership, remove_success, expected_status",
    [
        (True, True, status.HTTP_200_OK),
        (True, False, status.HTTP_500_INTERNAL_SERVER_ERROR),
        (False, True, status.HTTP_403_FORBIDDEN),
    ],
)
def test_delete_file(
    test_client,
    monkeypatch,
    ownership,
    remove_success,
    expected_status,
    mock_get_user_id,
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

    response = test_client.delete(get_file_url() + "/1")

    assert response.status_code == expected_status

    if ownership:
        assert mock_remove_file.called

    if not ownership:
        assert not mock_remove_file.called


def test_retrieve_file_binary_unowned_document(
    test_client, monkeypatch, mock_retrieve_binary_file_setup
):
    document_id, _, mock_get_document = mock_retrieve_binary_file_setup

    mock_document_owned_by_user = Mock(return_value=False)
    monkeypatch.setattr(
        "perry.api.endpoints.document.document_owned_by_user",
        mock_document_owned_by_user,
    )

    response = test_client.get(get_file_url() + "/" + str(document_id))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    mock_document_owned_by_user.assert_called_once()


def test_retrieve_file_binary_file_not_loaded(
    monkeypatch, test_client, mock_retrieve_binary_file_setup
):
    (
        document_id,
        mock_document_owned_by_user,
        mock_get_document,
    ) = mock_retrieve_binary_file_setup

    mock_load_file = Mock(side_effect=Exception("Database error"))
    monkeypatch.setattr("perry.api.endpoints.document.load_file", mock_load_file)
    response = test_client.get(get_file_url() + "/" + str(document_id))

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    mock_load_file.assert_called_once()
    mock_document_owned_by_user.assert_called_once()


def test_retrieve_file_binary_successful(
    monkeypatch, test_client, mock_retrieve_binary_file_setup
):
    (
        document_id,
        mock_document_owned_by_user,
        mock_get_document,
    ) = mock_retrieve_binary_file_setup

    mock_load_file = Mock(return_value=b"some_file_content")
    monkeypatch.setattr("perry.api.endpoints.document.load_file", mock_load_file)

    response = test_client.get(get_file_url() + "/" + str(document_id))
    content_dict = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert content_dict["filename"] == "filename.pdf"
    assert content_dict["file"] == "some_file_content"
    mock_load_file.assert_called_once()
    mock_document_owned_by_user.assert_called_once()
    mock_get_document.assert_called_once()


def test_should_return_document_when_authorized(
    test_client, mock_document_owned_by_user, mock_get_document, mock_get_user_id
):
    response = test_client.get(get_document_url() + "/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == mock_api_doc().dict()


def test_should_raise_403_when_unauthorized(
    test_client, monkeypatch, mock_get_document, mock_get_user_id
):
    monkeypatch.setattr(
        "perry.api.endpoints.document.document_owned_by_user",
        lambda *args, **kwargs: False,
    )
    response = test_client.get(get_document_url() + "/1")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_doc_raises_404_when_doc_not_found(
    test_client, monkeypatch, mock_document_owned_by_user, mock_get_user_id
):
    monkeypatch.setattr(
        "perry.api.endpoints.document.get_document",
        lambda *args, **kwargs: None,
    )
    response = test_client.get(get_document_url() + "/1")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_all_doc_info_returns_all_user_documents(
    test_client, mock_get_user_documents, mock_get_user_id
):
    response = test_client.get(get_document_url() + "/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [mock_api_doc().dict()]


def test_update_doc_description_should_return_200(
    test_client, mock_get_user_id, monkeypatch
):
    monkeypatch.setattr(
        "perry.api.endpoints.document.document_owned_by_user",
        lambda *args, **kwargs: True,
    )
    monkeypatch.setattr(
        "perry.api.endpoints.document.update_document",
        lambda *args, **kwargs: True,
    )
    doc_id = 1
    response = test_client.put(
        get_document_url() + "/" + str(doc_id),
        json=APIDocument(title="Test Document", id=doc_id, description="test").dict(),
    )
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.parametrize(
    "file_size, raise_http_error",
    [
        (10000000, False),
        (10000001, True),
    ],
)
def test_check_file_size(file_size, raise_http_error):
    if raise_http_error:
        with pytest.raises(HTTPException):
            check_file_size(file_size)
    else:
        check_file_size(file_size)


@pytest.mark.parametrize(
    "file_type, raise_http_error",
    [
        ("application/pdf", False),
        ("application/txt", True),
    ],
)
def test_check_file_type(file_type, raise_http_error):
    if raise_http_error:
        with pytest.raises(HTTPException):
            check_file_type(file_type)
    else:
        check_file_type(file_type)


@pytest.mark.parametrize(
    "doc_amount, raise_http_error",
    [
        (20, False),
        (21, True),
    ],
)
def test_check_max_documents(doc_amount, raise_http_error):
    user = Mock()
    user.documents = range(doc_amount)
    if raise_http_error:
        with pytest.raises(HTTPException):
            check_max_documents(user)
    else:
        check_max_documents(user)
