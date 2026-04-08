"""Idea analyzer node."""

from pathlib import Path
from typing import Literal

from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
)
from langchain_core.runnables import RunnableConfig, ensure_config
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

# Logging config
from log_config import setup_logging
from nodes.llm_config import get_model_name
from nodes.prompt_loader import load_prompt
from nodes.state import AgentState

logger = setup_logging(logger_name=__name__, log_file="idea_analyzer.log")

_NODE_DIR = Path(__file__).resolve().parent
IDEA_ANALYZER_PROMPT = load_prompt(_NODE_DIR)
STAGE_ROUTER_PROMPT = load_prompt(_NODE_DIR, "stage_router.txt")


class IdeaAnalyzerStage(BaseModel):
    """Idea analyzer stage."""

    workflow_stage: Literal["idea", "awaiting_confirm"] = Field(
        description=(
            "idea: user vague/no concrete idea;"
            " awaiting_confirm: concrete idea stated"
            "and assistant offered recap, tailored questions,"
            "and confirm-before-plan ask."
        )
    )


def _last_human_text(state: AgentState) -> str:
    """Get the last human text from the state."""
    for m in reversed(state.get("messages") or []):
        if isinstance(m, HumanMessage):
            c = m.content
            if isinstance(c, str):
                return c.strip()
            if isinstance(c, list) and c:
                return str(c[0])
    return ""


async def _invoke_model(
    model: ChatOpenAI,
    messages: list[BaseMessage],
    cfg: RunnableConfig,
) -> str:
    """Invoke the model."""
    raw_content = await model.ainvoke(messages, config=cfg)
    content = raw_content.content
    reply = content if isinstance(content, str) else str(content)
    return reply.strip()


async def idea_analyzer_node(
    state: AgentState,
    config: RunnableConfig | None = None,
):
    """Idea analyzer node."""

    # configure the model
    cfg = ensure_config(config)
    model = ChatOpenAI(model=get_model_name())

    # messages to the model
    system_message = SystemMessage(content=IDEA_ANALYZER_PROMPT)
    messages = [system_message, *state["messages"]]

    reply = await _invoke_model(model, messages, cfg)

    # if no reply, return fallback message this is edge case
    if not reply:
        fallback = (
            "Please share one concrete idea (a project, product, or topic) you'd like to explore."
        )
        logger.warning("idea_analyzer_node No reply, returning fallback message")
        return {"messages": [AIMessage(content=fallback)], "workflow_stage": "idea"}

    # route to the appropriate workflow stage
    router = ChatOpenAI(model=get_model_name(), temperature=0).with_structured_output(
        IdeaAnalyzerStage,
        method="function_calling",
        include_raw=True,
    )
    user_snippet = _last_human_text(state)
    logger.info("idea_analyzer_node User snippet: %s", user_snippet)

    # create human message for router
    router_human = HumanMessage(
        content=(f"User's latest message:\n{user_snippet or '(none)'}\n\nAssistant reply:\n{reply}")
    )
    router_sys = SystemMessage(content=STAGE_ROUTER_PROMPT)
    routed = await router.ainvoke([router_sys, router_human], config=cfg)
    logger.info("idea_analyzer_node Routed: %s", routed)
    parsed = routed["parsed"]
    if parsed is None:
        logger.error("idea_analyzer stage router parse failed: %s", routed.get("parsing_error"))
        wf = "idea"
    else:
        wf = parsed.workflow_stage

    msg = AIMessage(content=reply)
    return {"messages": [msg], "workflow_stage": wf}
