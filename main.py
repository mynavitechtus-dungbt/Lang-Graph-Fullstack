"""LangGraph entry: idea → confirm → plan (Markdown + Yes/No UI) → feedback."""

from dotenv import load_dotenv
from langgraph.graph import END, START, StateGraph

from nodes.confirmation.node import confirmation_handler
from nodes.idea_analyzer.node import idea_analyzer_node
from nodes.idea_helper.node import idea_helper_node
from nodes.plan.node import plan_node
from nodes.plan_feedback.node import plan_feedback_handler
from nodes.state import AgentState

load_dotenv()


def route_entry(state: AgentState) -> str:
    stage = state.get("workflow_stage") or "idea"
    # After a finished plan, new user messages start a fresh idea pass.
    if stage == "completed":
        return "idea"
    if stage == "awaiting_confirm":
        return "awaiting_confirm"
    if stage == "planning":
        return "planning"
    if stage == "awaiting_plan_feedback":
        return "awaiting_plan_feedback"
    if stage == "plan_revision":
        return "plan_revision"
    return "idea"


graph = StateGraph(AgentState)
graph.add_node("idea_analyzer", idea_analyzer_node)
graph.add_node("confirmation_handler", confirmation_handler)
graph.add_node("idea_helper", idea_helper_node)
graph.add_node("plan_node", plan_node)
graph.add_node("plan_feedback_handler", plan_feedback_handler)

graph.add_conditional_edges(
    START,
    route_entry,
    {
        "idea": "idea_analyzer",
        "awaiting_confirm": "confirmation_handler",
        "planning": "plan_node",
        "awaiting_plan_feedback": "plan_feedback_handler",
        "plan_revision": "plan_node",
    },
)

graph.add_edge("idea_analyzer", END)
graph.add_edge("idea_helper", END)
graph.add_edge("plan_node", END)

graph = graph.compile()
