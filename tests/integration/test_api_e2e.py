"""
End-to-end integration tests for the FastAPI API.

These tests require:
- Running Docker services (make dev)
- Seeded data (make seed-db)
- Valid OPENAI_API_KEY in .env

Run: RUN_INTEGRATION_TESTS=1 pytest tests/integration/test_api_e2e.py -v
"""

import pytest
import os
import requests
import json

API_BASE = os.getenv("API_BASE", "http://localhost:5000")

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_INTEGRATION_TESTS") != "1",
    reason="Integration tests disabled. Set RUN_INTEGRATION_TESTS=1 to run."
)


class TestHealthEndpoint:
    """Test health check endpoint."""
    
    def test_health_returns_200(self):
        response = requests.get(f"{API_BASE}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestQueryEndpoint:
    """Test /api/query endpoint."""
    
    def test_query_returns_response(self):
        response = requests.post(
            f"{API_BASE}/api/query",
            json={"query": "What tools help reduce documentation burden?"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "route" in data
        assert data["route"] in ("tool_finder", "org_matcher", "workflow_advisor")
        assert "response" in data
        assert len(data["response"]) > 0
    
    def test_query_missing_field_returns_422(self):
        """FastAPI returns 422 for validation errors."""
        response = requests.post(
            f"{API_BASE}/api/query",
            json={}
        )
        assert response.status_code == 422
        assert "detail" in response.json()


class TestThreadsEndpoint:
    """Test /api/threads CRUD endpoints."""
    
    def test_create_and_delete_thread(self):
        response = requests.post(
            f"{API_BASE}/api/threads",
            json={"title": "E2E Test Thread"}
        )
        assert response.status_code == 201
        thread = response.json()
        thread_id = thread["id"]
        assert thread["title"] == "E2E Test Thread"
        
        response = requests.delete(f"{API_BASE}/api/threads/{thread_id}")
        assert response.status_code == 200


class TestConfidenceScore:
    """Test confidence score in API responses."""
    
    def test_query_includes_confidence(self):
        """Verify confidence scores are returned in query response."""
        response = requests.post(
            f"{API_BASE}/api/query",
            json={"query": "How can we reduce physician burnout?"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "confidence" in data, "Response should include confidence scores"
        confidence = data["confidence"]
        
        assert "routing" in confidence, "Should have routing confidence"
        assert "retrieval" in confidence, "Should have retrieval confidence"
        assert "response" in confidence, "Should have response confidence"
        assert "overall" in confidence, "Should have overall confidence"
        
        for key, value in confidence.items():
            assert isinstance(value, (int, float)), f"{key} should be numeric"
            assert 0.0 <= value <= 1.0, f"{key} should be between 0 and 1"
    
    def test_thread_query_includes_confidence(self):
        """Verify confidence scores in thread query response."""
        response = requests.post(
            f"{API_BASE}/api/threads",
            json={"title": "Confidence Test"}
        )
        thread_id = response.json()["id"]
        
        response = requests.post(
            f"{API_BASE}/api/threads/{thread_id}/query",
            json={"query": "What hospitals use AI for oncology?"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "confidence" in data, "Thread query should include confidence"
        assert "overall" in data["confidence"]
        assert 0.0 <= data["confidence"]["overall"] <= 1.0
        
        requests.delete(f"{API_BASE}/api/threads/{thread_id}")
    
    def test_confidence_values_are_reasonable(self):
        """Confidence values should be in valid range."""
        response = requests.post(
            f"{API_BASE}/api/query",
            json={"query": "Find clinical documentation tools"}
        )
        data = response.json()
        
        if "confidence" in data:
            assert data["confidence"]["overall"] > 0.0, "Should have non-zero confidence"
            assert data["confidence"]["routing"] > 0.3, "Clear query should have decent routing confidence"
