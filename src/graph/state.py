from typing import TypedDict

from langchain_core.documents import Document


class GraphState(TypedDict):
    query: str
    question: str
    documents: list[Document]
    generation: str
    hallucination_retry_count: int
    search_retry_count: int
    grounded: bool
    relevant: bool
