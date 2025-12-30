from langchain_core.language_models import BaseChatModel
from langchain_core.messages import SystemMessage, HumanMessage

from src.agents.state import AgentState
from src.retrievers.base import BaseRetriever


WORKFLOW_ADVISOR_PROMPT = """You are a clinical workflow advisor synthesizing recommendations from tools and organizational insights.

Based on the retrieved clinical tools and healthcare organizations below, provide comprehensive workflow recommendations.

Retrieved Tools:
{tools}

Retrieved Organizations:
{orgs}

Provide actionable recommendations that combine tool capabilities with real-world implementation insights."""


class WorkflowAdvisorAgent:
    """Synthesizes recommendations from both tools and organizations."""
    
    def __init__(
        self, 
        tools_retriever: BaseRetriever, 
        orgs_retriever: BaseRetriever, 
        llm: BaseChatModel
    ):
        self.tools_retriever = tools_retriever
        self.orgs_retriever = orgs_retriever
        self.llm = llm
    
    def run(self, state: AgentState) -> AgentState:
        """Search both tables and generate comprehensive response."""
        tools_results = self.tools_retriever.search(state.query, limit=3)
        orgs_results = self.orgs_retriever.search(state.query, limit=3)
        
        state.tools_results = tools_results
        state.orgs_results = orgs_results
        
        tools_text = self._format_tools(tools_results)
        orgs_text = self._format_orgs(orgs_results)
        
        messages = [
            SystemMessage(content=WORKFLOW_ADVISOR_PROMPT.format(
                tools=tools_text, 
                orgs=orgs_text
            )),
            HumanMessage(content=state.query)
        ]
        
        response = self.llm.invoke(messages)
        state.response = response.content
        return state
    
    def _format_tools(self, results: list[dict]) -> str:
        """Format tool results for the prompt."""
        if not results:
            return "No tools found."
        
        lines = []
        for r in results:
            lines.append(f"- **{r['name']}**: {r['problem_solved']}")
        return "\n".join(lines)
    
    def _format_orgs(self, results: list[dict]) -> str:
        """Format org results for the prompt."""
        if not results:
            return "No organizations found."
        
        lines = []
        for r in results:
            lines.append(f"- **{r['name']}** ({r['specialty']}): {', '.join(r['ai_use_cases'])}")
        return "\n".join(lines)
