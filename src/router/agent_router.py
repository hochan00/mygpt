from fastapi import APIRouter

from src.graph.graph import graph
from src.schemas.agent_schema import (
    AgentRequest,
    AgentResponse,
)
from src.services import utils

router = APIRouter(tags=["Agent"])


@router.post("/agent", response_model=AgentResponse)
def query_rag_graph(req: AgentRequest):
    """LangGraph 기반 RAG 질문 답변"""
    result = graph.invoke({"question": req.question})
    sources = list({doc.metadata.get("source", "") for doc in result["documents"]})

    code_examples = []
    for doc in result["documents"]:
        code_examples.extend(utils.extract_code_blocks(doc.page_content))

    return AgentResponse(
        question=req.question,
        answer=result["generation"],
        sources=sources,
        code_examples=code_examples,
    )
