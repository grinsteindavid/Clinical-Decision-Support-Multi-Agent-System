from typing import Literal
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI

from src.config import OPENAI_API_KEY
from src.embeddings.openai_embed import get_embedding
from src.retrievers import ToolsRetriever, OrgsRetriever
from src.agents.state import AgentState, GraphState
from src.agents.supervisor import SupervisorAgent
from src.agents.tool_finder import ToolFinderAgent
from src.agents.org_matcher import OrgMatcherAgent
from src.agents.workflow_advisor import WorkflowAdvisorAgent


def create_clinical_graph(llm=None):
    """Create the clinical decision support multi-agent graph."""
    
    if llm is None:
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=OPENAI_API_KEY,
            temperature=0
        )
    
    tools_retriever = ToolsRetriever(embed_fn=get_embedding)
    orgs_retriever = OrgsRetriever(embed_fn=get_embedding)
    
    supervisor = SupervisorAgent(llm=llm)
    tool_finder = ToolFinderAgent(retriever=tools_retriever, llm=llm)
    org_matcher = OrgMatcherAgent(retriever=orgs_retriever, llm=llm)
    workflow_advisor = WorkflowAdvisorAgent(
        tools_retriever=tools_retriever,
        orgs_retriever=orgs_retriever,
        llm=llm
    )
    
    def supervisor_node(state: GraphState) -> dict:
        agent_state = AgentState.from_graph_state(state)
        result = supervisor.route(agent_state)
        return {"route": result.route}
    
    def tool_finder_node(state: GraphState) -> dict:
        agent_state = AgentState.from_graph_state(state)
        result = tool_finder.run(agent_state)
        return {
            "tools_results": result.tools_results,
            "response": result.response
        }
    
    def org_matcher_node(state: GraphState) -> dict:
        agent_state = AgentState.from_graph_state(state)
        result = org_matcher.run(agent_state)
        return {
            "orgs_results": result.orgs_results,
            "response": result.response
        }
    
    def workflow_advisor_node(state: GraphState) -> dict:
        agent_state = AgentState.from_graph_state(state)
        result = workflow_advisor.run(agent_state)
        return {
            "tools_results": result.tools_results,
            "orgs_results": result.orgs_results,
            "response": result.response
        }
    
    def route_decision(state: GraphState) -> Literal["tool_finder", "org_matcher", "workflow_advisor"]:
        return state.get("route", "workflow_advisor")
    
    graph = StateGraph(GraphState)
    
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("tool_finder", tool_finder_node)
    graph.add_node("org_matcher", org_matcher_node)
    graph.add_node("workflow_advisor", workflow_advisor_node)
    
    graph.set_entry_point("supervisor")
    
    graph.add_conditional_edges(
        "supervisor",
        route_decision,
        {
            "tool_finder": "tool_finder",
            "org_matcher": "org_matcher",
            "workflow_advisor": "workflow_advisor"
        }
    )
    
    graph.add_edge("tool_finder", END)
    graph.add_edge("org_matcher", END)
    graph.add_edge("workflow_advisor", END)
    
    return graph.compile()
