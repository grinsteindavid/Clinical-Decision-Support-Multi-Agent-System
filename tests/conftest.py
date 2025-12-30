import pytest
from langchain_core.messages import AIMessage

from tests.mocks.mock_embeddings import fake_embedding
from tests.mocks.mock_db import MockToolsRetriever, MockOrgsRetriever, MOCK_TOOLS, MOCK_ORGS


class FakeLLM:
    """Fake LLM for unit tests - no API calls."""
    
    def __init__(self, response: str = "This is a test response."):
        self.response = response
        self.calls = []
    
    def invoke(self, messages):
        self.calls.append(messages)
        return AIMessage(content=self.response)


@pytest.fixture
def fake_llm():
    """Provide a fake LLM that returns predefined responses."""
    return FakeLLM()


@pytest.fixture
def routing_llm():
    """Fake LLM that returns routing decisions."""
    return FakeLLM(response="tool_finder")


@pytest.fixture
def mock_tools_retriever():
    """Provide mock tools retriever with fixture data."""
    return MockToolsRetriever(MOCK_TOOLS)


@pytest.fixture
def mock_orgs_retriever():
    """Provide mock orgs retriever with fixture data."""
    return MockOrgsRetriever(MOCK_ORGS)


@pytest.fixture
def sample_query():
    """Sample query for testing."""
    return "How can we reduce documentation burden for physicians?"
