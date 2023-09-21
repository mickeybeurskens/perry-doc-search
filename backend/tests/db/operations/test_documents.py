import pytest
from pathlib import Path
import io
from unittest.mock import Mock, patch
from perry.db.operations.documents import *
from perry.db.operations.users import get_user


@pytest.fixture
def mock_bytes_obj():
    return io.BytesIO(b"Some binary data here")


@pytest.fixture
def mock_file_path(tmp_path):
    return Path(tmp_path / "1.txt")


@pytest.fixture
def mocked_document(tmpdir):
    mock_document = Mock()
    temp_file_path = tmpdir / "temp_file.txt"
    mock_document.file_path = str(temp_file_path)
    return mock_document


def add_dummy_document(db_session: Session, file_path: str):
    doc = Document(file_path=file_path)
    db_session.add(doc)
    db_session.commit()
    db_session.refresh(doc)
    return doc.id


def setup_test_db_and_files(test_db, path, name, new_path):
    os.makedirs(new_path.parent, exist_ok=True)
    doc_id = add_dummy_document(test_db, str(path))
    return doc_id


def assert_file_movement(test_db, doc, original_path, new_path):
    assert original_path.exists()
    assert not new_path.exists()
    move_file(test_db, doc.id, str(new_path))
    assert not original_path.exists()
    assert new_path.exists()
    assert doc.file_path == str(new_path)


def test_save_file_success(mock_bytes_obj, mock_file_path, test_db, tmpdir):
    with patch(
        "perry.db.operations.documents.get_file_storage_path", return_value=str(tmpdir)
    ):
        doc_id = save_file(db_session=test_db, bytes_obj=mock_bytes_obj, suffix="txt")
        doc = test_db.query(Document).filter(Document.id == doc_id).first()
        assert doc.file_path == str(mock_file_path)
        assert Path(doc.file_path).exists()


from unittest.mock import patch, Mock


def test_remove_file_success(test_db, mocked_document):
    # Setup: Mock the database object and file path
    with patch(
        "perry.db.operations.documents.get_document"
    ) as mock_get_document, patch(
        "perry.db.operations.documents.delete_document"
    ) as mock_delete_document:
        mock_get_document.return_value = mocked_document

        with open(mocked_document.file_path, "w") as f:
            f.write("temporary file content")

        remove_file(db_session=test_db, document_id=1)

        assert not Path(mocked_document.file_path).exists()
        mock_delete_document.assert_called_with(test_db, 1)


def test_load_file_success(test_db, mocked_document):
    # Setup: Mock the database object and file path
    with patch("perry.db.operations.documents.get_document") as mock_get_document:
        mock_get_document.return_value = mocked_document

        file_content = b"temporary file content"
        with open(mocked_document.file_path, "wb") as f:
            f.write(file_content)

        loaded_content = load_file(db_session=test_db, document_id=1)

        assert loaded_content.getbuffer() == file_content


@pytest.mark.parametrize(
    "temp_files",
    [
        [{"name": "file1", "contents": "file1 contents", "suffix": ".tmp"}],
        [{"name": "file2", "contents": "file2 contents", "suffix": ".tmp"}],
        [{"name": "file3", "contents": "file3 contents", "suffix": ".tmp"}],
    ],
    indirect=True,
)
def test_move_file_success(test_db, tmpdir, temp_files):
    for file_info in temp_files:
        original_path = Path(file_info["path"])
        name = file_info["name"]
        new_path = Path(tmpdir / "new" / f"{name}.tmp")

        doc_id = setup_test_db_and_files(test_db, original_path, name, new_path)
        doc = get_document(test_db, doc_id)
        assert_file_movement(test_db, doc, original_path, new_path)


def test_create_document(test_db):
    created_document_id = create_document(test_db)
    test_db.commit()

    assert created_document_id is not None


def test_get_document(test_db, add_document_to_db):
    doc_id = add_document_to_db()

    retrieved_document = get_document(test_db, doc_id)

    assert retrieved_document.id == doc_id


def test_get_non_existent_document_should_return_none(test_db):
    retrieved_document = get_document(test_db, -1)

    assert retrieved_document is None


def test_delete_document(test_db, add_document_to_db):
    created_document_id = add_document_to_db()

    delete_document(test_db, created_document_id)
    retrieved_document = get_document(test_db, created_document_id)

    assert retrieved_document is None


def test_remove_user_from_document(test_db, add_document_to_db, create_user_in_db):
    username = "galahad"
    password = "wise"
    created_document_id = add_document_to_db()
    created_user_id = create_user_in_db(username=username, password=password)
    update_document(test_db, created_document_id, user_ids=[created_user_id])

    user = get_user(test_db, created_user_id)
    document = get_document(test_db, created_document_id)

    assert user in document.users

    update_document(test_db, document.id, user_ids=[])

    assert user not in document.users


def test_document_title_description_should_update(test_db: Session, add_document_to_db):
    doc_id = add_document_to_db()
    update_document(test_db, doc_id, title="New Title", description="New Description")
    updated_doc = get_document(test_db, doc_id)
    assert updated_doc.title == "New Title"
    assert updated_doc.description == "New Description"


def test_document_conversations_should_update(
    test_db, add_document_to_db, add_conversation_to_db
):
    doc_id = add_document_to_db()
    conversation_ids = [add_conversation_to_db(), add_conversation_to_db()]
    update_document(test_db, doc_id, conversation_ids=conversation_ids)
    updated_doc = get_document(test_db, doc_id)
    assert set(c.id for c in updated_doc.conversations) == set(conversation_ids)


def test_document_users_should_update(test_db, add_document_to_db, create_user_in_db):
    doc_id = add_document_to_db()
    user_ids = [
        create_user_in_db(username="hari", password="seldon"),
        create_user_in_db(username="psychohistory", password="foundation"),
    ]
    update_document(test_db, doc_id, user_ids=user_ids)
    updated_doc = get_document(test_db, doc_id)
    assert set(u.id for u in updated_doc.users) == set(user_ids)


def test_update_document_invalid_id(test_db):
    assert update_document(test_db, -1, title="New Title") is None


def test_update_document_none_empty_params(test_db, add_document_to_db):
    doc_id = add_document_to_db()
    title = "First Foundation"
    update_document(test_db, doc_id, title=title)
    update_document(test_db, doc_id, title=None)
    updated_doc = get_document(test_db, doc_id)
    assert updated_doc.title == title
    update_document(test_db, doc_id, conversation_ids=[])
    assert len(updated_doc.conversations) == 0


def test_owned_correctly_returns_true(test_db, add_document_to_db, create_user_in_db):
    doc_id = add_document_to_db()
    user_id = create_user_in_db(username="owner", password="password")
    update_document(test_db, doc_id, user_ids=[user_id])
    assert document_owned_by_user(test_db, doc_id, user_id)


def test_owned_non_owned_document_returns_false(
    test_db, add_document_to_db, create_user_in_db
):
    doc_id = add_document_to_db()
    user_id = create_user_in_db(username="owner", password="password")
    assert not document_owned_by_user(test_db, doc_id, user_id)


def test_owned_non_existing_user_returns_false(test_db, add_document_to_db):
    doc_id = add_document_to_db()
    assert not document_owned_by_user(test_db, doc_id, -1)


def test_owned_non_existing_document_returns_false(test_db, create_user_in_db):
    user_id = create_user_in_db(username="owner", password="password")
    assert not document_owned_by_user(test_db, -1, user_id)


def test_owned_non_existing_user_and_document_returns_false(test_db):
    assert not document_owned_by_user(test_db, -1, -1)
