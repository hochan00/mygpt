from fastapi import APIRouter

from src.graph.graph import graph
from src.schemas.agent_schema import (
    AgentRequest,
    AgentResponse,
)

router = APIRouter(tags=["Agent"])


@router.post("/agent", response_model=AgentResponse)
def agent_graph(req: AgentRequest):
    """Agent 기반 노션 작업 비서"""
    result = graph.invoke(
        {"messages": [("user", req.message)]},
        config={"configurable": {"thread_id": req.thread_id}},
    )

    return AgentResponse(
        message=result["message"][-1].content,
    )
