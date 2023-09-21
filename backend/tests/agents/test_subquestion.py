import pytest
from pathlib import Path
from tests.agents.fixtures_subquestion import *
from llama_index.query_engine import SubQuestionQueryEngine


def test_doc_paths_from_connected_docs_should_be_returned(
    create_subquestion_agent_with_documents,
):
    file_info = [
        {"content": "test", "name": "test", "suffix": ".pdf"},
        {"content": "test2", "name": "test2", "suffix": ".pdf"},
    ]
    agent, document_ids, file_paths = create_subquestion_agent_with_documents(
        file_info=file_info
    )
    source_data_paths = agent._get_doc_paths()
    assert list(source_data_paths.keys()) == document_ids
    for path in file_paths:
        path = Path(path)
        assert path in source_data_paths.values()
        path.is_file()


def test_should_return_empty_dict_when_no_docs_in_directory(
    create_subquestion_agent,
):
    result = create_subquestion_agent()._load_docs()
    assert result == {}


def test_should_group_single_pdf_by_filename(create_subquestion_agent_with_documents):
    file_info = [
        {"content": "test", "name": "single", "suffix": ".pdf"},
    ]
    agent, document_ids, _ = create_subquestion_agent_with_documents(
        file_info=file_info
    )
    result = agent._load_docs()
    assert document_ids == list(result.keys())
    assert [len(result[id]) == 1 for id in document_ids]


def test_should_group_multiple_pdfs_with_same_filename_together(
    create_subquestion_agent_with_documents,
):
    file_info = [
        {"content": "test", "name": "duplicate", "suffix": ".pdf"},
        {"content": "test", "name": "duplicate", "suffix": ".pdf"},
    ]
    agent, document_ids, _ = create_subquestion_agent_with_documents(
        file_info=file_info
    )
    result = agent._load_docs()
    assert document_ids == list(result.keys())
    assert len(result.keys()) == 2


def test_should_raise_exception_for_non_pdf_file(
    create_subquestion_agent_with_documents,
):
    file_info = [
        {"content": "test", "name": "textfile", "suffix": ".txt"},
        {"content": "test", "name": "pdffile", "suffix": ".pdf"},
    ]
    with pytest.raises(Exception, match=r".*is not a PDF"):
        agent, _, _ = create_subquestion_agent_with_documents(file_info=file_info)
        agent._load_docs()


def test_cache_exists_raises_error_if_directory_not_found(monkeypatch):
    monkeypatch.setattr(Path, "exists", lambda x: False)
    directory = Path("/some/random/directory")
    assert not SubquestionAgent._cache_exists(directory)


def test_cache_exists_passes_when_all_files_and_directory_exist(monkeypatch):
    monkeypatch.setattr(Path, "exists", lambda x: True)
    directory = Path("/some/random/directory")

    try:
        SubquestionAgent._cache_exists(directory)
    except FileNotFoundError:
        pytest.fail("FileNotFoundError raised when it shouldn't be.")


@pytest.mark.parametrize(
    "cache_exists, expected_call", [(True, "_load_index"), (False, "_create_index")]
)
def test_get_vector_indexes_should_call_appropriate_methods_based_on_cache_existence(
    monkeypatch, cache_exists, expected_call, create_subquestion_agent
):
    mock_doc_sets = {1: ["doc1"], 2: ["doc2"]}
    mock_load_index = lambda self, doc_id: f"Loaded {doc_id}"
    mock_create_index = lambda self, doc_id, doc_set=None: f"Created {doc_id}"

    monkeypatch.setattr(SubquestionAgent, "_cache_exists", lambda self, x: cache_exists)
    monkeypatch.setattr(SubquestionAgent, "_load_index", mock_load_index)
    monkeypatch.setattr(SubquestionAgent, "_create_index", mock_create_index)

    agent = create_subquestion_agent()
    result = agent._get_vector_indexes(mock_doc_sets)

    assert result is not None
    assert isinstance(result, dict)

    for doc_id in mock_doc_sets.keys():
        expected_output = (
            getattr(agent, expected_call)(doc_id, mock_doc_sets.get(doc_id))
            if expected_call == "_create_index"
            else getattr(agent, expected_call)(doc_id)
        )
        assert result[doc_id] == expected_output


@pytest.mark.parametrize(
    "missing_file",
    ["docstore.json", "index_store.json", "graph_store.json", "vector_store.json"],
)
def test_cache_exists_should_return_false_when_required_file_is_missing(
    monkeypatch, missing_file
):
    def mock_exists(path):
        return not path.name == missing_file

    monkeypatch.setattr(Path, "exists", mock_exists)
    directory = Path("/some/random/directory")

    assert not SubquestionAgent._cache_exists(directory)


def test_load_index_should_raise_error_if_cache_does_not_exist(
    monkeypatch, create_subquestion_agent
):
    monkeypatch.setattr(Path, "exists", lambda x: False)

    with pytest.raises(
        FileNotFoundError,
        match=r"Vector index for document_id: .* not found in cache .*",
    ):
        agent = create_subquestion_agent()
        agent._load_index(1)


def test_create_subquestion_engine_should_return_valid_SubQuestionQueryEngine(
    monkeypatch, create_subquestion_agent_with_documents
):
    file_info = [
        {"content": "test", "name": "duplicate", "suffix": ".pdf"},
        {"content": "test", "name": "duplicate", "suffix": ".pdf"},
    ]

    mock_subquestion_query_engine = "MockedSubQuestionQueryEngine"

    def mock_from_defaults(query_engine_tools, service_context):
        return mock_subquestion_query_engine

    agent, _, _ = create_subquestion_agent_with_documents(file_info)

    assert isinstance(agent._create_engine(), MockSubQuestionQueryEngine)
