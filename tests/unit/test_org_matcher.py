import pytest

from src.agents.state import AgentState
from src.agents.org_matcher import OrgMatcherAgent
from tests.conftest import FakeLLM
from tests.mocks.mock_db import MockOrgsRetriever, MOCK_ORGS


class TestOrgMatcherAgent:
    
    def test_searches_and_returns_results(self):
        retriever = MockOrgsRetriever(MOCK_ORGS)
        llm = FakeLLM(response="Here are relevant healthcare organizations...")
        agent = OrgMatcherAgent(retriever=retriever, llm=llm)
        
        state = AgentState(query="hospitals using AI for cardiology")
        result = agent.run(state)
        
        assert len(result.orgs_results) > 0
        assert result.response == "Here are relevant healthcare organizations..."
    
    def test_passes_query_to_retriever(self):
        retriever = MockOrgsRetriever(MOCK_ORGS)
        llm = FakeLLM()
        agent = OrgMatcherAgent(retriever=retriever, llm=llm)
        
        state = AgentState(query="cancer treatment centers")
        result = agent.run(state)
        
        assert len(result.orgs_results) == len(MOCK_ORGS)
    
    def test_formats_results_for_llm(self):
        retriever = MockOrgsRetriever(MOCK_ORGS)
        llm = FakeLLM()
        agent = OrgMatcherAgent(retriever=retriever, llm=llm)
        
        state = AgentState(query="test query")
        agent.run(state)
        
        messages = llm.calls[0]
        system_message = messages[0].content
        
        assert "Mayo Clinic" in system_message
        assert "Multi-specialty" in system_message
    
    def test_handles_empty_results(self):
        retriever = MockOrgsRetriever(fixture_data=[])
        llm = FakeLLM(response="No organizations found.")
        agent = OrgMatcherAgent(retriever=retriever, llm=llm)
        
        state = AgentState(query="something obscure")
        result = agent.run(state)
        
        assert result.orgs_results == []
