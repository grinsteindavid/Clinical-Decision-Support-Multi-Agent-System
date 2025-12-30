import pytest
from src.agents.state import AgentState


class TestAgentState:
    
    def test_create_state_with_query(self):
        state = AgentState(query="test query")
        assert state.query == "test query"
        assert state.route is None
        assert state.tools_results == []
        assert state.orgs_results == []
        assert state.response == ""
        assert state.error is None
    
    def test_state_with_route(self):
        state = AgentState(query="test", route="tool_finder")
        assert state.route == "tool_finder"
    
    def test_state_with_results(self):
        state = AgentState(
            query="test",
            tools_results=[{"name": "Tool1"}],
            orgs_results=[{"name": "Org1"}]
        )
        assert len(state.tools_results) == 1
        assert len(state.orgs_results) == 1
    
    def test_state_with_response(self):
        state = AgentState(query="test", response="Here is the answer.")
        assert state.response == "Here is the answer."
    
    def test_state_with_error(self):
        state = AgentState(query="test", error="Something went wrong")
        assert state.error == "Something went wrong"
