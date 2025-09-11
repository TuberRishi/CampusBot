from typing import List, TypedDict

from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    """
    Defines the state for the agent graph.
    This state is passed between all nodes in the graph.
    """
    original_query: str
    language: str
    refined_query: str
    answer: str
    source: str
    # Chat history will be used in Phase 2
    chat_history: List[BaseMessage]
