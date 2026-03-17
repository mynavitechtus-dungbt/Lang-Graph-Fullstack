import os
from pathlib import Path

from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, MessagesState, StateGraph

from log_config import setup_logging

logger = setup_logging(log_file='app.log', logger_name=__name__)


async def mock_llm(state: MessagesState):
    """Mock LLM response"""
    logger.info(
        "mock_llm: bắt đầu xử lý, số tin nhắn=%d", len(state["messages"])
    )
    model = ChatOpenAI(model="gpt-4.1-mini")
    system_message = SystemMessage(content="You are a helpful assistant.")
    response = await model.ainvoke([system_message, *state["messages"]])
    logger.info("mock_llm: đã nhận phản hồi từ LLM")
    return {"messages": response}

graph = StateGraph(MessagesState)
graph.add_node(mock_llm)
graph.add_edge(START, "mock_llm")
graph.add_edge("mock_llm", END)
graph = graph.compile()

