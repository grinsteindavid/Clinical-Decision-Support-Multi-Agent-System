from abc import ABC, abstractmethod
from typing import Protocol


class EmbeddingFunction(Protocol):
    """Protocol for embedding functions (real or mock)."""
    def __call__(self, text: str) -> list[float]: ...


class BaseRetriever(ABC):
    """Abstract base class for pgvector retrievers."""
    
    def __init__(self, embed_fn: EmbeddingFunction):
        self.embed_fn = embed_fn
    
    @abstractmethod
    def search(self, query: str, limit: int = 5) -> list[dict]:
        """Search for similar items using semantic search."""
        pass
