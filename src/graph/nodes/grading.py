from pydantic import BaseModel, Field

from src.core.llm import get_llm
from src.graph.state import GraphState
from src.services.prompts import GRADE_DOCUMENTS, GRADE_HALLUCINATION_PROMPT
from src.services.utils import format_docs


class HallucinationGrade(BaseModel):
    grounded: bool = Field(description="답변이 문서 내용에 근거하면 true, 아니면 false")


class DocumentsGrade(BaseModel):
    relevant: bool = Field(
        description="검색한 문서 내용이 질문과 관련이 있으면 true, 없으면 false"
    )


def grade_hallucination(state: GraphState) -> dict:
    documents = state["documents"]
    generation = state["generation"]
    hallucination_retry_count = state.get("hallucination_retry_count", 0)

    structured_llm = get_llm().with_structured_output(HallucinationGrade)
    chain = GRADE_HALLUCINATION_PROMPT | structured_llm
    result = chain.invoke({"context": format_docs(documents), "generation": generation})

    return {
        "hallucination_retry_count": hallucination_retry_count + 1,
        "grounded": result.grounded,
    }


def route_hallucination_result(state: GraphState) -> str:
    if state.get("grounded", False):
        return "end"
    if state.get("hallucination_retry_count", 0) >= 2:
        return "refuse"
    return "retry"


def grade_documents(state: GraphState) -> dict:
    query = state.get("query", state["question"])
    documents = state["documents"]
    search_retry_count = state.get("search_retry_count", 0)

    structured_llm = get_llm().with_structured_output(DocumentsGrade)
    chain = GRADE_DOCUMENTS | structured_llm
    result = chain.invoke({"query": query, "documents": format_docs(documents)})

    return {"search_retry_count": search_retry_count + 1, "relevant": result.relevant}


def route_documents_result(state: GraphState) -> str:
    if state.get("relevant", False):
        return "generate"
    if state.get("search_retry_count", 0) >= 2:
        return "refuse"
    return "transform"
