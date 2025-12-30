import pytest
from langchain_core.messages import AIMessage

from src.agents.state import AgentState
from src.agents.supervisor import SupervisorAgent
from tests.conftest import FakeLLM


class TestSupervisorAgent:
    
    def test_routes_to_tool_finder(self):
        llm = FakeLLM(response="tool_finder")
        supervisor = SupervisorAgent(llm=llm)
        
        state = AgentState(query="What tools help with documentation?")
        result = supervisor.route(state)
        
        assert result.route == "tool_finder"
        assert len(llm.calls) == 1
    
    def test_routes_to_org_matcher(self):
        llm = FakeLLM(response="org_matcher")
        supervisor = SupervisorAgent(llm=llm)
        
        state = AgentState(query="Which hospitals use AI for sepsis detection?")
        result = supervisor.route(state)
        
        assert result.route == "org_matcher"
    
    def test_routes_to_workflow_advisor(self):
        llm = FakeLLM(response="workflow_advisor")
        supervisor = SupervisorAgent(llm=llm)
        
        state = AgentState(query="How should we implement AI to reduce burnout?")
        result = supervisor.route(state)
        
        assert result.route == "workflow_advisor"
    
    def test_defaults_to_workflow_advisor_on_invalid_route(self):
        llm = FakeLLM(response="invalid_route")
        supervisor = SupervisorAgent(llm=llm)
        
        state = AgentState(query="Some query")
        result = supervisor.route(state)
        
        assert result.route == "workflow_advisor"
    
    def test_handles_uppercase_response(self):
        llm = FakeLLM(response="TOOL_FINDER")
        supervisor = SupervisorAgent(llm=llm)
        
        state = AgentState(query="Some query")
        result = supervisor.route(state)
        
        assert result.route == "tool_finder"
