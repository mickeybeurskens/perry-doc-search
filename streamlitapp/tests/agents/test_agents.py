import pytest
from perry.agents.single_directory_vector import SingleDirectoryVectorAgent


class TestSingleDirectoryVectorAgent:
    """ Tests the SingleDirectoryVectorAgent. """
    def test_answer_query(self):
        """ Answer query should return a string. """
        agent = SingleDirectoryVectorAgent()
        assert type(agent.answer_query("Hello World!")) == str

    def test_set_document_directory(self):
        """ Set document directory should return None. """
        agent = SingleDirectoryVectorAgent()
        assert agent.set_document_directory("Hello World!") == None

    def test_get_name(self):
        """ Get name should return a string. """
        agent = SingleDirectoryVectorAgent()
        assert type(agent.get_name()) == str

    def test_get_description(self):
        """ Get description should return a string. """
        agent = SingleDirectoryVectorAgent()
        assert type(agent.get_description()) == str