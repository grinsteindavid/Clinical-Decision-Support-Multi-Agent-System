import pytest

from src.agents.state import AgentState
from src.agents.tool_finder import ToolFinderAgent
from tests.conftest import FakeLLM
from tests.mocks.mock_db import MockToolsRetriever, MOCK_TOOLS


class TestToolFinderAgent:
    
    def test_searches_and_returns_results(self):
        retriever = MockToolsRetriever(MOCK_TOOLS)
        llm = FakeLLM(response="Based on your query, I recommend...")
        agent = ToolFinderAgent(retriever=retriever, llm=llm)
        
        state = AgentState(query="reduce documentation burden")
        result = agent.run(state)
        
        assert len(result.tools_results) > 0
        assert result.response == "Based on your query, I recommend..."
    
    def test_passes_query_to_retriever(self):
        retriever = MockToolsRetriever(MOCK_TOOLS)
        llm = FakeLLM()
        agent = ToolFinderAgent(retriever=retriever, llm=llm)
        
        state = AgentState(query="drug interaction checking")
        result = agent.run(state)
        
        assert len(result.tools_results) == len(MOCK_TOOLS)
    
    def test_formats_results_for_llm(self):
        retriever = MockToolsRetriever(MOCK_TOOLS)
        llm = FakeLLM()
        agent = ToolFinderAgent(retriever=retriever, llm=llm)
        
        state = AgentState(query="test query")
        agent.run(state)
        
        messages = llm.calls[0]
        system_message = messages[0].content
        
        assert "Ambient Clinical Documentation AI" in system_message
        assert "Documentation" in system_message
    
    def test_handles_empty_results(self):
        retriever = MockToolsRetriever(fixture_data=[])
        llm = FakeLLM(response="No tools found matching your query.")
        agent = ToolFinderAgent(retriever=retriever, llm=llm)
        
        state = AgentState(query="something obscure")
        result = agent.run(state)
        
        assert result.tools_results == []
        assert "No tools found" in result.response
