from fastapi import APIRouter, File, UploadFile

from src.schema import (
    RAGRequest,
    RAGResponse,
)
from src.services import document_store, rag_service

router = APIRouter(tags=["RAG"])


@router.post("/documents")
async def add_documents(file: UploadFile = File(...)):
    """RAG 문서 등록"""
    content = await file.read()
    text = content.decode("utf-8")
    chunk_count = await document_store.add_documents(text=text, source=file.filename)
    return {
        "message": f"'{file.filename}' 문서가 등록되었습니다.",
        "chunks": chunk_count,
    }


@router.post("/rag", response_model=RAGResponse)
async def query_rag(req: RAGRequest):
    """RAG 기반 질문 답변"""
    result = await rag_service.query_rag(req.question)
    return RAGResponse(question=req.question, **result)
