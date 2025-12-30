from langchain_core.language_models import BaseChatModel
from langchain_core.messages import SystemMessage, HumanMessage

from src.agents.state import AgentState
from src.retrievers.base import BaseRetriever


ORG_MATCHER_PROMPT = """You are a healthcare organizations specialist helping find relevant case studies and implementations.

Based on the retrieved healthcare organizations below, provide insights about how similar organizations are using AI.

Retrieved Organizations:
{orgs}

Provide a concise summary of relevant implementations and lessons learned."""


class OrgMatcherAgent:
    """Finds relevant healthcare organizations with AI implementations."""
    
    def __init__(self, retriever: BaseRetriever, llm: BaseChatModel):
        self.retriever = retriever
        self.llm = llm
    
    def run(self, state: AgentState) -> AgentState:
        """Search for organizations and generate response."""
        results = self.retriever.search(state.query, limit=5)
        state.orgs_results = results
        
        orgs_text = self._format_results(results)
        
        messages = [
            SystemMessage(content=ORG_MATCHER_PROMPT.format(orgs=orgs_text)),
            HumanMessage(content=state.query)
        ]
        
        response = self.llm.invoke(messages)
        state.response = response.content
        return state
    
    def _format_results(self, results: list[dict]) -> str:
        """Format search results for the prompt."""
        if not results:
            return "No organizations found."
        
        lines = []
        for r in results:
            lines.append(f"- **{r['name']}** ({r['specialty']})")
            lines.append(f"  Type: {r['org_type']} | Location: {r['city']}, {r['state']}")
            lines.append(f"  AI Use Cases: {', '.join(r['ai_use_cases'])}")
            lines.append(f"  Similarity: {r['similarity']:.2f}")
            lines.append("")
        return "\n".join(lines)
