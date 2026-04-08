"""LangGraph state: CopilotKit messages + workflow stage."""

from copilotkit import CopilotKitState


# CopilotKitState is a TypedDict at runtime; stubs do not model `total` inheritance.
class AgentState(CopilotKitState, total=False):  # type: ignore[call-arg]
    """workflow_stage drives routing from START (optional when total=False)."""

    workflow_stage: str
