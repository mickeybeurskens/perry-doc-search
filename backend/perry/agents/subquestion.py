import asyncio
import os
from pathlib import Path
from llama_index import (
    Document,
    SimpleDirectoryReader,
    VectorStoreIndex,
    ServiceContext,
    StorageContext,
    load_index_from_storage,
    Prompt,
)
from llama_index.tools import QueryEngineTool, ToolMetadata
from llama_index.llms import OpenAI
from llama_index.llms.base import LLM
from llama_index.query_engine import SubQuestionQueryEngine
from llama_index.callbacks import CallbackManager, LlamaDebugHandler
from dotenv import load_dotenv
import openai
from sqlalchemy.orm import Session

from perry.agents.base import BaseAgent, BaseAgentConfig
from perry.db.models import Document as DBDocument, User as DBUser, Agent as DBAgent
from perry.db.operations.documents import get_document


class SubquestionConfig(BaseAgentConfig):
    """Configuration for the SubquestionAgent."""

    name: str
    language_model_name: str
    temperature: float


class SubquestionAgent(BaseAgent):
    """An agent that queries a set of indexed documents by posing subquestions."""

    _cache_path = Path(".cache")

    def _setup(self):
        self._service_context = self._get_new_service_context(
            self._get_new_model(
                self.config.language_model_name, self.config.temperature
            )
        )
        self._engine = self._create_engine()

    async def query(self, query: str) -> str:
        return await self._engine.aquery(query)

    def _on_save(self):
        pass

    @classmethod
    def _on_load(
        cls, db_session: Session, config: SubquestionConfig, agent_id: int
    ) -> BaseAgent:
        return cls(db_session, config, agent_id)

    @classmethod
    @staticmethod
    def _get_config_instance(config_data: dict) -> SubquestionConfig:
        return SubquestionConfig(**config_data)

    @staticmethod
    def _get_new_model(model: str, temperature: float) -> LLM:
        load_dotenv()
        openai.api_key = os.getenv("OPENAI_API_KEY")
        return OpenAI(temperature=temperature, model=model)

    @staticmethod
    def _get_new_service_context(llm: OpenAI) -> ServiceContext:
        return ServiceContext.from_defaults(
            llm=llm,
        )

    def _get_doc_paths(self) -> dict[int, Path]:
        """Return a list of paths to the documents in the conversation with ids as dictionary keys."""
        documents = self._agent_data.conversation.documents
        doc_paths = {}
        for document in documents:
            doc_path = Path(document.file_path)
            self._validate_pdf_path(doc_path)
            doc_paths[document.id] = doc_path
        return doc_paths

    def _validate_pdf_path(self, doc_path: Path):
        if not doc_path.is_file():
            raise Exception(
                f"The specified path '{doc_path}' does not point to a file."
            )
        if doc_path.suffix.lower() != ".pdf":
            raise Exception(f"The file at '{doc_path}' is not a PDF.")

    def _create_engine(self):
        docs_grouped = self._load_docs()
        doc_vector_indexes = self._get_vector_indexes(docs_grouped)

        return self._create_subquestion_engine(doc_vector_indexes)

    def _load_docs(self) -> dict[int, list[Document]]:
        file_paths = self._get_doc_paths()
        if not file_paths:
            return {}

        reader = SimpleDirectoryReader(input_files=file_paths.values())
        pages = reader.load_data()
        pages_grouped = self._group_pages_by_filename(pages)

        return self._group_docs_by_id(file_paths, pages_grouped)

    def _group_pages_by_filename(
        self, pages: list[Document]
    ) -> dict[str, list[Document]]:
        pages_grouped = {}
        for page in pages:
            file_name = page.metadata.get("file_name", "NO_FILE_NAME")
            pages_grouped.setdefault(file_name, []).append(page)
        return pages_grouped

    def _group_docs_by_id(
        self, file_paths: dict[int, Path], pages_grouped: dict[str, list[Document]]
    ) -> dict[int, list[Document]]:
        docs_grouped = {}
        for doc_id, doc_path in file_paths.items():
            file_name = doc_path.name
            if file_name in pages_grouped:
                docs_grouped[doc_id] = pages_grouped[file_name]
            else:
                raise Exception(f"Pages not found for file {file_name}")
        return docs_grouped

    def _get_vector_indexes(
        self, doc_sets: dict[int, list[Document]]
    ) -> dict[int, VectorStoreIndex]:
        indexes_info = {}

        for doc_id in doc_sets.keys():
            save_path = Path(self._cache_path, str(doc_id))

            if self._cache_exists(save_path):
                indexes_info[doc_id] = self._load_index(doc_id)
            else:
                indexes_info[doc_id] = self._create_index(doc_id, doc_sets[doc_id])
        return indexes_info

    @staticmethod
    def _cache_exists(directory: Path) -> bool:
        if not directory.exists():
            return False
        if not Path(directory, "docstore.json").exists():
            return False
        if not Path(directory, "index_store.json").exists():
            return False
        if not Path(directory, "graph_store.json").exists():
            return False
        if not Path(directory, "vector_store.json").exists():
            return False
        return True

    def _load_index(self, doc_id: int) -> VectorStoreIndex:
        save_path = Path(self._cache_path, str(doc_id))
        try:
            print(
                f"Loading vector index for document_id: {doc_id} from cache for {self.__class__.__name__}"
            )
            storage_context = StorageContext.from_defaults(
                persist_dir=save_path,
            )
            return load_index_from_storage(storage_context)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Vector index for document_id: {doc_id} not found in cache {save_path}"
            )

    def _create_index(self, doc_id: int, doc_set: list[Document]) -> VectorStoreIndex:
        index = VectorStoreIndex.from_documents(
            doc_set, service_context=self._service_context
        )
        index.storage_context.persist(persist_dir=Path(self._cache_path, str(doc_id)))
        return index

    def _create_subquestion_engine(
        self, doc_indexes: dict[int, VectorStoreIndex]
    ) -> SubQuestionQueryEngine:
        tools = []
        for doc_id in doc_indexes.keys():
            summary = get_document(self._db_session, doc_id).description
            tools.append(
                QueryEngineTool(
                    query_engine=doc_indexes[doc_id].as_query_engine(
                        service_context=self._service_context
                    ),
                    metadata=ToolMetadata(name=doc_id, description=summary),
                )
            )
        return SubQuestionQueryEngine.from_defaults(
            query_engine_tools=tools,
            service_context=self._service_context,
        )
