import pathlib
from abc import ABC, abstractmethod
from perry.messages import MessageHistory


class Agent(ABC):
    """ Answers queries about a set of documents in a particular way. """
    document_directory: pathlib.Path
    message_history: MessageHistory
    name: str
    description: str

    def __init__(self, document_directory: pathlib.Path) -> None:
        self.document_directory = document_directory

    @abstractmethod
    def answer_query(self, query: str) -> str:
        """ Answers a query. """
        pass

