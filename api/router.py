from fastapi import APIRouter, File, UploadFile

from api.graph.graph import graph
from api.schema import (
    AutoregressiveRequest,
    AutoregressiveResponse,
    RAGRequest,
    RAGResponse,
)
from api.services import autoregressive_service, rag_service

router = APIRouter()


@router.post(
    "/autoregressive", response_model=AutoregressiveResponse, tags=["Autoregressive"]
)
async def generate_autoregressive(req: AutoregressiveRequest):
    """autoregressive 텍스트 생성"""
    generated_text = await autoregressive_service.generate_autoregressive(
        prompt=req.prompt,
        max_length=req.max_length,
        temperature=req.temperature,
        top_k=req.top_k,
    )
    return AutoregressiveResponse(prompt=req.prompt, generated_text=generated_text)


@router.post("/documents", tags=["RAG"])
async def add_documents(file: UploadFile = File(...)):
    """RAG 문서 등록"""
    content = await file.read()
    text = content.decode("utf-8")
    chunk_count = await rag_service.add_documents(text=text, source=file.filename)
    return {
        "message": f"'{file.filename}' 문서가 등록되었습니다.",
        "chunks": chunk_count,
    }


@router.post("/rag", response_model=RAGResponse, tags=["RAG"])
async def query_rag(req: RAGRequest):
    """RAG 기반 질문 답변"""
    result = await rag_service.query_rag(req.question)
    return RAGResponse(question=req.question, **result)


@router.post("/rag/graph", response_model=RAGResponse, tags=["LangGraph"])
def query_rag_graph(req: RAGRequest):
    """LangGraph 기반 RAG 질문 답변"""
    result = graph.invoke({"question": req.question})
    sources = list({doc.metadata.get("source", "") for doc in result["documents"]})

    code_examples = []
    for doc in result["documents"]:
        code_examples.extend(rag_service.extract_code_blocks(doc.page_content))

    return RAGResponse(
        question=req.question,
        answer=result["generation"],
        sources=sources,
        code_examples=code_examples,
    )
