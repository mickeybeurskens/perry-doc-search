import pytest
from pathlib import Path
from perry.agents.subquestion import SubquestionAgent, SubquestionConfig
from perry.db.operations.documents import update_document


def get_subquestion_config():
    return SubquestionConfig(name="test", language_model_name="test", temperature=0.3)


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


@pytest.mark.parametrize(
    "temp_files",
    [
        [
            {"name": "file1", "contents": "Hello1", "suffix": ".pdf"},
            {"name": "file2", "contents": "Hello2", "suffix": ".pdf"},
        ]
    ],
    indirect=True,
)
def test_doc_paths_from_connected_docs_should_be_returned(
    temp_files, create_subquestion_agent_with_documents
):
    file_paths = [temp_file["path"] for temp_file in temp_files]
    agent, document_ids = create_subquestion_agent_with_documents(file_paths=file_paths)
    assert len(agent._source_data_paths) == len(document_ids)
    for path in file_paths:
        path = Path(path)
        assert path in agent._source_data_paths
        path.is_file()
