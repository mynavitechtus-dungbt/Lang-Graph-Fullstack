"""LangGraph entry: idea → confirm → plan (Markdown + Yes/No UI) → feedback."""

from dotenv import load_dotenv
from langgraph.graph import END, START, StateGraph

from nodes.confirmation.node import confirmation_handler
from nodes.idea_analyzer.node import idea_analyzer_node
from nodes.idea_helper.node import idea_helper_node
from nodes.plan.node import plan_node
from nodes.plan_feedback.node import plan_feedback_handler
from nodes.state import AgentState
from workflow_stage import WorkflowStage, coerce_workflow_stage

load_dotenv()


def route_entry(state: AgentState) -> WorkflowStage:
    """Route the entry point to the appropriate stage."""
    stage = coerce_workflow_stage(state.get("workflow_stage", WorkflowStage.IDEA))

    if stage.is_next():
        return stage

    if stage.is_back():
        return WorkflowStage.IDEA

    return WorkflowStage.IDEA


_builder = StateGraph(AgentState)
_builder.add_node("idea_analyzer", idea_analyzer_node)
_builder.add_node("confirmation_handler", confirmation_handler)
_builder.add_node("idea_helper", idea_helper_node)
_builder.add_node("plan_node", plan_node)
_builder.add_node("plan_feedback_handler", plan_feedback_handler)

_builder.add_conditional_edges(
    START,
    route_entry,
    {
        WorkflowStage.IDEA: "idea_analyzer",
        WorkflowStage.AWAITING_CONFIRM: "confirmation_handler",
        WorkflowStage.PLANNING: "plan_node",
        WorkflowStage.AWAITING_PLAN_FEEDBACK: "plan_feedback_handler",
        WorkflowStage.PLAN_REVISION: "plan_node",
    },
)

_builder.add_edge("idea_analyzer", END)
_builder.add_edge("idea_helper", END)
_builder.add_edge("plan_node", END)

graph = _builder.compile()
