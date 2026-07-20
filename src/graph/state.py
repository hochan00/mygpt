from typing import TypedDict

from langchain_core.documents import Document
from langgraph.graph import MessagesState


class AgentState(MessagesState):
    pass


class GraphState(TypedDict):
    query: str
    question: str
    documents: list[Document]
    generation: str
    hallucination_retry_count: int
    search_retry_count: int
    grounded: bool
    relevant: bool
