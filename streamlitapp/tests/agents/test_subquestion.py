import pytest
from pathlib import Path
from fpdf import FPDF
from perry.agents.subquestion import SubquestionAgent, SubquestionConfig
from perry.db.operations.documents import update_document


def get_subquestion_config():
    return SubquestionConfig(name="test", language_model_name="test", temperature=0.3)


def create_temp_file(tmp_path: Path, content: str, name: str, suffix: str) -> Path:
    temp_file_path = tmp_path / Path(name + suffix.lower())
    if suffix.lower() == ".pdf":
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, content, ln=1, align="C")

        pdf.output(name=temp_file_path, dest="F")

        return str(temp_file_path)
    else:
        # Create a temporary file
        temp_file_path = tmp_path / Path(name + suffix)
        with open(temp_file_path, "w") as f:
            f.write(content)
        return str(temp_file_path)


@pytest.fixture(scope="function")
def create_subquestion_agent(
    test_db, add_connected_agent_conversation_to_db
) -> SubquestionAgent:
    """Add an agent to the database and return its ID."""

    def _create_agent():
        agent_id, conversation_id = add_connected_agent_conversation_to_db()
        agent = SubquestionAgent(
            test_db,
            get_subquestion_config(),
            agent_id,
        )
        return agent

    return _create_agent


@pytest.fixture(scope="function")
def create_subquestion_agent_with_documents(
    test_db,
    add_documents_with_file_names,
    add_connected_agent_conversation_to_db,
    tmp_path,
):
    def _create_subquestion_agent_with_documents(file_info: list[dict[str, str, str]]):
        file_paths = [
            create_temp_file(
                tmp_path, file_info["content"], file_info["name"], file_info["suffix"]
            )
            for file_info in file_info
        ]

        agent_id, conversation_id = add_connected_agent_conversation_to_db()
        document_ids = add_documents_with_file_names(file_paths)
        for document_id in document_ids:
            update_document(test_db, document_id, conversation_ids=[conversation_id])
        agent = SubquestionAgent(
            test_db,
            get_subquestion_config(),
            agent_id,
        )
        return agent, document_ids, file_paths

    return _create_subquestion_agent_with_documents


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
    assert len(source_data_paths) == len(document_ids)
    for path in file_paths:
        path = Path(path)
        assert path in source_data_paths
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
    agent, _, _ = create_subquestion_agent_with_documents(file_info=file_info)
    result = agent._load_docs()
    assert "single.pdf" in result.keys()
    assert len(result["single.pdf"]) == 1


def test_should_group_multiple_pdfs_with_same_filename_together(
    create_subquestion_agent_with_documents,
):
    file_info = [
        {"content": "test", "name": "duplicate", "suffix": ".pdf"},
        {"content": "test", "name": "duplicate", "suffix": ".pdf"},
    ]
    agent, _, _ = create_subquestion_agent_with_documents(file_info=file_info)
    result = agent._load_docs()
    assert "duplicate.pdf" in result.keys()
    assert len(result["duplicate.pdf"]) == 2


def test_should_raise_exception_for_non_pdf_file(create_subquestion_agent_with_documents):
    file_info = [
        {"content": "test", "name": "textfile", "suffix": ".txt"},
        {"content": "test", "name": "pdffile", "suffix": ".pdf"},
    ]
    with pytest.raises(Exception, match=r".*should be a PDF file"):
        agent, _, _ = create_subquestion_agent_with_documents(file_info=file_info)
        
