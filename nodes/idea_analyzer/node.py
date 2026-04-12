"""Idea analyzer node."""

from pathlib import Path
from typing import Literal, cast

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.runnables.config import RunnableConfig, ensure_config, merge_configs
from langchain_openai import ChatOpenAI
from langgraph.constants import TAG_NOSTREAM
from pydantic import BaseModel, Field

# Logging config
from log_config import setup_logging
from nodes.llm_config import get_model_name
from nodes.message_utils import ensure_openai_tool_roundtrip
from nodes.prompt_loader import load_prompt
from nodes.state import AgentState

logger = setup_logging(logger_name=__name__, log_file="idea_analyzer.log")

_NODE_DIR = Path(__file__).resolve().parent
IDEA_ANALYZER_PROMPT = load_prompt(_NODE_DIR)
STAGE_ROUTER_PROMPT = load_prompt(_NODE_DIR, "stage_router.txt")


class IdeaAnalyzerStage(BaseModel):
    """Stage router output (second call only)."""

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
) -> AIMessage:
    """Invoke the model (streams to LangGraph when config has no TAG_NOSTREAM).

    Returns the same ``AIMessage`` instance (optionally ``model_copy``) so ``id``
    matches the streamed run; LangGraph's message stream dedupes on_chain_end vs
    on_llm_end when ids match.
    """
    raw = await model.ainvoke(messages, config=cfg)
    if not isinstance(raw, AIMessage):
        return AIMessage(content=str(raw))
    content = raw.content
    if isinstance(content, str):
        stripped = content.strip()
        if stripped != content:
            return raw.model_copy(update={"content": stripped})
        return raw
    return raw


async def idea_analyzer_node(
    state: AgentState,
    config: RunnableConfig | None = None,
):
    """Idea analyzer: streamed reply, then silent stage classification."""

    cfg = ensure_config(config)
    model = ChatOpenAI(model=get_model_name())

    system_message = SystemMessage(content=IDEA_ANALYZER_PROMPT)
    history = ensure_openai_tool_roundtrip(list(state.get("messages") or []))
    messages = [system_message, *history]

    # Main reply: do NOT use TAG_NOSTREAM — LangGraph forwards LLM token streams to the UI.
    assistant_msg = await _invoke_model(model, messages, cfg)
    reply_text = (
        assistant_msg.content
        if isinstance(assistant_msg.content, str)
        else str(assistant_msg.content)
    )
    reply_text = reply_text.strip()

    if not reply_text:
        fallback = (
            "Please share one concrete idea (a project, product, or topic) you'd like to explore."
        )
        logger.warning("idea_analyzer_node No reply, returning fallback message")
        return {"messages": [AIMessage(content=fallback)], "workflow_stage": "idea"}

    router = ChatOpenAI(model=get_model_name(), temperature=0).with_structured_output(
        IdeaAnalyzerStage,
        method="function_calling",
        include_raw=False,
    )
    user_snippet = _last_human_text(state)
    router_human = HumanMessage(
        content=(
            f"User's latest message:\n{user_snippet or '(none)'}\n\nAssistant reply:\n{reply_text}"
        )
    )
    router_sys = SystemMessage(content=STAGE_ROUTER_PROMPT)
    silent_cfg = merge_configs(cfg, {"tags": [TAG_NOSTREAM]})
    routed = await router.ainvoke([router_sys, router_human], config=silent_cfg)
    wf = cast(IdeaAnalyzerStage, routed).workflow_stage
    logger.info("idea_analyzer_node workflow_stage=%s", wf)

    # Reuse the streamed message's id so StreamMessagesHandler skips duplicate emit.
    return {"messages": [assistant_msg], "workflow_stage": wf}
