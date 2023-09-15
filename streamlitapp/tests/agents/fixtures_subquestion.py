import pytest
from llama_index.llms.mock import MockLLM
from llama_index.embeddings.langchain import LangchainEmbedding
from langchain.embeddings.fake import FakeEmbeddings
from llama_index import ServiceContext
from perry.agents.subquestion import SubquestionAgent, SubquestionConfig
from fpdf import FPDF
from pathlib import Path
from perry.db.operations.documents import update_document


def create_mock_llm():
    return MockLLM(max_tokens=10)


def create_mock_embedding_model():
    return LangchainEmbedding(
        langchain_embedding=FakeEmbeddings(size=768),
    )


def create_mock_service_context(*args, **kwargs):
    return ServiceContext.from_defaults(
        llm=create_mock_llm(),
        embed_model=create_mock_embedding_model(),
    )


@pytest.fixture(scope="function", autouse=True)
def mock_subquestion_agent_service_context(monkeypatch):
    monkeypatch.setattr(
        "perry.agents.subquestion.SubquestionAgent._get_new_service_context",
        create_mock_service_context,
    )


def get_subquestion_config():
    return SubquestionConfig(name="test", language_model_name="test", temperature=0.3).dict()


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
) -> tuple[SubquestionAgent, list[int], list[str]]:
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
