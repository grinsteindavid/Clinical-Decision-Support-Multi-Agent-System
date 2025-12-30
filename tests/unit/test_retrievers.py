import pytest

from tests.mocks.mock_embeddings import fake_embedding
from tests.mocks.mock_db import MockToolsRetriever, MockOrgsRetriever, MOCK_TOOLS, MOCK_ORGS


class TestFakeEmbedding:
    
    def test_returns_1536_dimensions(self):
        embedding = fake_embedding("test text")
        assert len(embedding) == 1536
    
    def test_returns_floats(self):
        embedding = fake_embedding("test")
        assert all(isinstance(x, float) for x in embedding)
    
    def test_values_between_0_and_1(self):
        embedding = fake_embedding("test")
        assert all(0 <= x <= 1 for x in embedding)
    
    def test_deterministic(self):
        embedding1 = fake_embedding("same text")
        embedding2 = fake_embedding("same text")
        assert embedding1 == embedding2
    
    def test_different_text_different_embedding(self):
        embedding1 = fake_embedding("text one")
        embedding2 = fake_embedding("text two")
        assert embedding1 != embedding2


class TestMockToolsRetriever:
    
    def test_returns_fixture_data(self):
        retriever = MockToolsRetriever(MOCK_TOOLS)
        results = retriever.search("any query")
        assert len(results) == len(MOCK_TOOLS)
    
    def test_respects_limit(self):
        retriever = MockToolsRetriever(MOCK_TOOLS)
        results = retriever.search("query", limit=1)
        assert len(results) == 1
    
    def test_returns_expected_fields(self):
        retriever = MockToolsRetriever(MOCK_TOOLS)
        results = retriever.search("query")
        
        result = results[0]
        assert "name" in result
        assert "category" in result
        assert "description" in result
        assert "similarity" in result


class TestMockOrgsRetriever:
    
    def test_returns_fixture_data(self):
        retriever = MockOrgsRetriever(MOCK_ORGS)
        results = retriever.search("any query")
        assert len(results) == len(MOCK_ORGS)
    
    def test_respects_limit(self):
        retriever = MockOrgsRetriever(MOCK_ORGS)
        results = retriever.search("query", limit=2)
        assert len(results) == 2
    
    def test_returns_expected_fields(self):
        retriever = MockOrgsRetriever(MOCK_ORGS)
        results = retriever.search("query")
        
        result = results[0]
        assert "name" in result
        assert "org_type" in result
        assert "specialty" in result
        assert "ai_use_cases" in result
        assert "similarity" in result
