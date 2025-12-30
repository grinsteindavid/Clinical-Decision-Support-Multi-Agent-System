from src.retrievers.base import BaseRetriever, EmbeddingFunction
from src.db.connection import get_connection


class OrgsRetriever(BaseRetriever):
    """Retriever for clinical_organizations table."""
    
    def __init__(self, embed_fn: EmbeddingFunction):
        super().__init__(embed_fn)
    
    def search(self, query: str, limit: int = 5) -> list[dict]:
        """Search clinical organizations by semantic similarity."""
        query_embedding = self.embed_fn(query)
        
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        id,
                        name,
                        org_type,
                        specialty,
                        description,
                        city,
                        state,
                        ai_use_cases,
                        1 - (embedding <=> %s::vector) AS similarity
                    FROM clinical_organizations
                    ORDER BY embedding <=> %s::vector
                    LIMIT %s
                """, (query_embedding, query_embedding, limit))
                return cur.fetchall()
