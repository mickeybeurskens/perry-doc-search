from io import BytesIO
import base64
import pytest
from pathlib import Path
from fpdf import FPDF
from perry.agents.subquestion import SubquestionAgent, SubquestionConfig
from perry.db.operations.documents import update_document


def get_subquestion_config():
    return SubquestionConfig(name="test", language_model_name="test", temperature=0.3)


def create_temp_pdf(tmp_path: Path, content: str, name: str) -> Path:
    temp_file_path = tmp_path / Path(name + ".pdf")
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, content, ln=1, align="C")
    
    pdf.output(name=temp_file_path, dest="F")
    
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
):
    def _create_subquestion_agent_with_documents(file_paths: list[str]):
        agent_id, conversation_id = add_connected_agent_conversation_to_db()
        document_ids = add_documents_with_file_names(file_paths)
        for document_id in document_ids:
            update_document(test_db, document_id, conversation_ids=[conversation_id])
        agent = SubquestionAgent(
            test_db,
            get_subquestion_config(),
            agent_id,
        )
        return agent, document_ids

    return _create_subquestion_agent_with_documents


def test_doc_paths_from_connected_docs_should_be_returned(
    tmp_path, create_subquestion_agent_with_documents
):
    file_info = [
        {"content": "test", "name": "test"},
        {"content": "test2", "name": "test2"},
    ]
    file_paths = [create_temp_pdf(tmp_path, file_info["content"], file_info["name"]) for file_info in file_info]
    agent, document_ids = create_subquestion_agent_with_documents(file_paths=file_paths)
    source_data_paths = agent._get_doc_paths()
    assert len(source_data_paths) == len(document_ids)
    for path in file_paths:
        path = Path(path)
        assert path in source_data_paths
        path.is_file()
