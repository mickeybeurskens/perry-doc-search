import pytest
from pathlib import Path
from tests.agents.fixtures_subquestion import *


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
