from langchain_core.language_models import BaseChatModel
from langchain_core.messages import SystemMessage, HumanMessage

from src.agents.state import AgentState
from src.retrievers.base import BaseRetriever


TOOL_FINDER_PROMPT = """You are a clinical tools specialist helping healthcare organizations find the right solutions.

Based on the retrieved clinical tools below, provide a helpful response to the user's query.
Focus on how each tool addresses their specific needs.

Retrieved Tools:
{tools}

Provide a concise, actionable recommendation."""


class ToolFinderAgent:
    """Finds relevant clinical decision support tools."""
    
    def __init__(self, retriever: BaseRetriever, llm: BaseChatModel):
        self.retriever = retriever
        self.llm = llm
    
    def run(self, state: AgentState) -> AgentState:
        """Search for tools and generate response."""
        results = self.retriever.search(state.query, limit=5)
        state.tools_results = results
        
        tools_text = self._format_results(results)
        
        messages = [
            SystemMessage(content=TOOL_FINDER_PROMPT.format(tools=tools_text)),
            HumanMessage(content=state.query)
        ]
        
        response = self.llm.invoke(messages)
        state.response = response.content
        return state
    
    def _format_results(self, results: list[dict]) -> str:
        """Format search results for the prompt."""
        if not results:
            return "No tools found."
        
        lines = []
        for r in results:
            lines.append(f"- **{r['name']}** ({r['category']})")
            lines.append(f"  Description: {r['description']}")
            lines.append(f"  Problem Solved: {r['problem_solved']}")
            lines.append(f"  Similarity: {r['similarity']:.2f}")
            lines.append("")
        return "\n".join(lines)
