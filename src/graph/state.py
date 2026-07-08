from typing import TypedDict

from langchain_core.documents import Document


class GraphState(TypedDict):
    question: str
    documents: list[Document]
    generation: str
    retry_count: int
