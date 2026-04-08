"""Workflow stage labels for AgentState.workflow_stage and START routing."""

from enum import StrEnum


class WorkflowStage(StrEnum):
    """Workflow stage labels for AgentState.workflow_stage and START routing."""

    IDEA = "idea"
    AWAITING_CONFIRM = "awaiting_confirm"
    PLANNING = "planning"
    AWAITING_PLAN_FEEDBACK = "awaiting_plan_feedback"
    PLAN_REVISION = "plan_revision"
    COMPLETED = "completed"

    def is_next(self) -> bool:
        """Check if the stage is a next stage."""
        return self in NEXT_STAGES

    def is_back(self) -> bool:
        """Check if the stage is a back stage."""
        return self in BACK_STAGES


NEXT_STAGES: frozenset[WorkflowStage] = frozenset[WorkflowStage](
    {
        WorkflowStage.AWAITING_CONFIRM,
        WorkflowStage.PLANNING,
        WorkflowStage.AWAITING_PLAN_FEEDBACK,
        WorkflowStage.PLAN_REVISION,
    }
)

BACK_STAGES: frozenset[WorkflowStage] = frozenset[WorkflowStage](
    {
        WorkflowStage.IDEA,
        WorkflowStage.COMPLETED,
    }
)


def coerce_workflow_stage(
    value: object,
    default: WorkflowStage = WorkflowStage.IDEA,
) -> WorkflowStage:
    """Normalize state values to WorkflowStage (TypedDict stores str; routing uses enum)."""
    if isinstance(value, WorkflowStage):
        return value
    try:
        return WorkflowStage(str(value))
    except ValueError:
        return default
