from fastapi import APIRouter

from src.graph.graph import graph
from src.schema import (
    RAGRequest,
    RAGResponse,
)
from src.services import utils

router = APIRouter(tags=["Agent"])


@router.post("/agent", response_model=RAGResponse)
def query_rag_graph(req: RAGRequest):
    """LangGraph 기반 RAG 질문 답변"""
    result = graph.invoke({"question": req.question})
    sources = list({doc.metadata.get("source", "") for doc in result["documents"]})

    code_examples = []
    for doc in result["documents"]:
        code_examples.extend(utils.extract_code_blocks(doc.page_content))

    return RAGResponse(
        question=req.question,
        answer=result["generation"],
        sources=sources,
        code_examples=code_examples,
    )
