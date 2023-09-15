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
from llama_index.query_engine import SubQuestionQueryEngine
from llama_index.callbacks import CallbackManager, LlamaDebugHandler
from dotenv import load_dotenv
import openai
from sqlalchemy.orm import Session

from perry.agents.base import BaseAgent, BaseAgentConfig
from perry.db.models import Document as DBDocument, User as DBUser, Agent as DBAgent


class SubquestionConfig(BaseAgentConfig):
    """Configuration for the SubquestionAgent."""

    name: str
    language_model_name: str
    temperature: float


class SubquestionAgent(BaseAgent):
    """An agent that queries a set of indexed documents by posing subquestions."""

    def _setup(self):
        load_dotenv()

        # self._cache_path = cache_dir
        # self._from_cache = from_cache

        # openai.api_key = os.getenv("OPENAI_API_KEY")
        # llm = OpenAI(temperature=0.3, model="gpt-4")

        # # llama_debug = LlamaDebugHandler(print_trace_on_end=True)
        # # callback_manager = CallbackManager([llama_debug])
        # self._service_context = ServiceContext.from_defaults(
        #     llm=llm,
        #     # callback_manager=callback_manager,
        # )

        self._engine = self._create_engine()

    async def query(self, query: str) -> str:
        return self._engine.aquery(query)

    def _on_save(self):
        pass

    @classmethod
    def _on_load(
        cls, db_session: Session, config: SubquestionConfig, agent_id: int
    ) -> BaseAgent:
        return cls(db_session, config, agent_id)

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
            raise Exception(f"The specified path '{doc_path}' does not point to a file.")
        if doc_path.suffix.lower() != ".pdf":
            raise Exception(f"The file at '{doc_path}' is not a PDF.")


    def _create_engine(self):
        pass
        # docs_grouped = self._load_docs()
        # doc_vector_indexes = self._get_vector_indexes(docs_grouped)
        # print(docs_grouped)

    #     return self._create_subquestion_engine(doc_indexes, file_summaries)

    def _load_docs(self) -> dict[int, list[Document]]:
        file_paths = self._get_doc_paths()
        if not file_paths:
            return {}

        reader = SimpleDirectoryReader(input_files=file_paths.values())
        pages = reader.load_data()
        pages_grouped = self._group_pages_by_filename(pages)

        return self._group_docs_by_id(file_paths, pages_grouped)

    def _group_pages_by_filename(self, pages: list[Document]) -> dict[str, list[Document]]:
        pages_grouped = {}
        for page in pages:
            file_name = page.metadata.get("file_name", "NO_FILE_NAME")
            pages_grouped.setdefault(file_name, []).append(page)
        return pages_grouped

    def _group_docs_by_id(self, file_paths: dict[int, Path], pages_grouped: dict[str, list[Document]]) -> dict[int, list[Document]]:
        docs_grouped = {}
        for doc_id, doc_path in file_paths.items():
            file_name = doc_path.name
            if file_name in pages_grouped:
                docs_grouped[doc_id] = pages_grouped[file_name]
            else:
                raise Exception(f"Pages not found for file {file_name}")
        return docs_grouped
    
    def _get_vector_indexes(
        self, doc_sets: dict[str, list[Document]]
    ) -> dict[str, VectorStoreIndex]:
        indexes_info = {}

        for name in doc_sets.keys():
            if self._from_cache:
                pass
            else:
                pass

    # def _load_indexes(self, doc_id: int) -> VectorStoreIndex:
    #     try:
    #         print(f"Loading index for {doc_path} from cache for {self.__class__.__name__}")
    #         storage_context = StorageContext.from_defaults(
    #             persist_dir=Path(doc_path),
    #         )
    #         return load_index_from_storage(storage_context)
    #     except FileNotFoundError:
    #         raise FileNotFoundError(f"Index for {doc_path} not found in cache at location")

    # def _create_indexes(self, doc_id: int, doc_set: list[Document]) -> VectorStoreIndex:

    #     index = VectorStoreIndex.from_documents(
    #         doc_set,
    #         service_context=self._service_context
    #     )
    #     index.storage_context.persist(persist_dir=Path(self._cache_path, doc_path))
    #     return str(doc_path), index

    # def _get_file_summaries(self, file_paths: list[Path]) -> dict[str, str]:
    #     file_summaries = {}
    #     for file_path in file_paths:
    #         meta_file_path = Path(file_path.parent, file_path.stem + ".txt")
    #         with open(meta_file_path, 'r') as f:
    #             file_summaries[meta_file_path.stem + ".pdf"] = f.read()
    #     return file_summaries

    # def _create_subquestion_engine(self, doc_indexes: dict[str, VectorStoreIndex], file_summaries: dict[str, str]):
    #     tools = []
    #     for name in doc_indexes.keys():
    #         if name in file_summaries.keys():
    #             summary = file_summaries[name]
    #             tools.append(QueryEngineTool(
    #                 query_engine=doc_indexes[name].as_query_engine(service_context=self._service_context),
    #                 metadata=ToolMetadata(name=name, description=summary)
    #             ))
    #         else:
    #             raise Exception(f"Summary not found for file {name}")
    #     return SubQuestionQueryEngine.from_defaults(
    #         query_engine_tools=tools,
    #         service_context=self._service_context,
    #     )
