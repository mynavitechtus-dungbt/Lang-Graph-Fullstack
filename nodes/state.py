"""LangGraph state: CopilotKit messages + workflow stage."""

from typing_extensions import NotRequired

from copilotkit import CopilotKitState


class AgentState(CopilotKitState, total=False):
    """workflow_stage drives routing from START."""

    workflow_stage: NotRequired[str]
