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

    def _get_doc_paths(self) -> list[Path]:
        documents = self._agent_data.conversation.documents
        doc_paths = []
        for document in documents:
            doc_path = Path(document.file_path)

            if not doc_path.is_file():
                raise Exception(f"Source data '{doc_path}' is not a file")
            if not doc_path.suffix.lower() == ".pdf":
                raise Exception(f"Source data '{doc_path}' should be a PDF file")
            doc_paths.append(doc_path)
        return doc_paths

    def _create_engine(self):
        docs_grouped = self._load_docs()
        print(docs_grouped)
    #     doc_indexes = self._create_file_indexes(docs_grouped)
    #     return self._create_subquestion_engine(doc_indexes, file_summaries)

    def _load_docs(self) -> dict[str, list[Document]]:
        docs_grouped = {}
        file_paths = self._get_doc_paths()
        if len(file_paths) == 0:
            return docs_grouped
        
        reader = SimpleDirectoryReader(input_files=file_paths)
        docs = reader.load_data()
        for doc in docs:
            if doc.metadata.get("file_name") is None:
                file_name = "NO_FILE_NAME"
            else:
                file_name = doc.metadata["file_name"]
            if file_name not in docs_grouped.keys():
                docs_grouped[file_name] = []
            docs_grouped[file_name].append(doc)
        return docs_grouped

    # def _create_file_indexes(self, doc_sets: dict[str, list[Document]]) -> dict[str, VectorStoreIndex]:
    #     indexes_info = {}

    #     for name in doc_sets.keys():
    #         if self._from_cache:
    #             try:
    #                 print(f"Loading index for {name} from cache for {self.__class__.__name__}")
    #                 storage_context = StorageContext.from_defaults(
    #                     persist_dir=Path(self._cache_path, name),
    #                 )
    #                 index = load_index_from_storage(storage_context)
    #             except FileNotFoundError:
    #                 raise FileNotFoundError(f"Index for {name} not found in cache at location '{Path(self._cache_path, name)}'")
    #         else:
    #             index = VectorStoreIndex.from_documents(
    #                 doc_sets[name],
    #                 service_context=self._service_context
    #             )
    #             index.storage_context.persist(persist_dir=Path(self._cache_path, name))
    #         indexes_info[name] = index

    #     return indexes_info

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

  