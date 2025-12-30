"""
End-to-end integration tests for the clinical decision support graph.

These tests require:
- Running Docker database (docker-compose up -d)
- Seeded data (python scripts/seed_db.py)
- Valid OPENAI_API_KEY in .env

Run separately: pytest tests/integration -v
"""

import pytest
import os

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_INTEGRATION_TESTS") != "1",
    reason="Integration tests disabled. Set RUN_INTEGRATION_TESTS=1 to run."
)


class TestGraphEndToEnd:
    """Integration tests that hit real DB and API."""
    
    def test_tool_finder_query(self):
        from src.agents.graph import create_clinical_graph
        
        graph = create_clinical_graph()
        result = graph.invoke({
            "query": "How can we reduce documentation burden?",
            "route": None,
            "tools_results": [],
            "orgs_results": [],
            "response": "",
            "error": None
        })
        
        assert result.get("route") in ("tool_finder", "workflow_advisor")
        assert len(result.get("response", "")) > 0
    
    def test_org_matcher_query(self):
        from src.agents.graph import create_clinical_graph
        
        graph = create_clinical_graph()
        result = graph.invoke({
            "query": "Which health systems are using AI for cardiology?",
            "route": None,
            "tools_results": [],
            "orgs_results": [],
            "response": "",
            "error": None
        })
        
        assert result.get("route") in ("org_matcher", "workflow_advisor")
        assert len(result.get("response", "")) > 0
    
    def test_workflow_advisor_query(self):
        from src.agents.graph import create_clinical_graph
        
        graph = create_clinical_graph()
        result = graph.invoke({
            "query": "How should we implement AI to address clinician burnout?",
            "route": None,
            "tools_results": [],
            "orgs_results": [],
            "response": "",
            "error": None
        })
        
        assert result.get("route") == "workflow_advisor"
        assert len(result.get("tools_results", [])) > 0 or len(result.get("orgs_results", [])) > 0
