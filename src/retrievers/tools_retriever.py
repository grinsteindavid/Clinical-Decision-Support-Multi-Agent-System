from src.retrievers.base import BaseRetriever, EmbeddingFunction
from src.db.connection import get_connection


class ToolsRetriever(BaseRetriever):
    """Retriever for clinical_tools table."""
    
    def __init__(self, embed_fn: EmbeddingFunction):
        super().__init__(embed_fn)
    
    def search(self, query: str, limit: int = 5) -> list[dict]:
        """Search clinical tools by semantic similarity."""
        query_embedding = self.embed_fn(query)
        
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        id,
                        name,
                        category,
                        description,
                        target_users,
                        problem_solved,
                        1 - (embedding <=> %s::vector) AS similarity
                    FROM clinical_tools
                    ORDER BY embedding <=> %s::vector
                    LIMIT %s
                """, (query_embedding, query_embedding, limit))
                return cur.fetchall()
