from fastapi import APIRouter, UploadFile, File

from api.schema import AutoregressiveRequest, AutoregressiveResponse, RAGRequest, RAGResponse
from api.services import autoregressive_service, rag_service

router = APIRouter()


@router.post("/autoregressive", response_model=AutoregressiveResponse, tags=["Autoregressive"])
async def generate_autoregressive(req: AutoregressiveRequest):
    generated_text = await autoregressive_service.generate_autoregressive(
        prompt=req.prompt,
        max_length=req.max_length,
        temperature=req.temperature,
        top_k=req.top_k,
    )
    return AutoregressiveResponse(prompt=req.prompt, generated_text=generated_text)


@router.post("/documents", tags=["RAG"])
async def add_documents(file: UploadFile = File(...)):
    content = await file.read()
    text = content.decode("utf-8")
    chunk_count = await rag_service.add_documents(text=text, source=file.filename)
    return {"message": f"'{file.filename}' 문서가 등록되었습니다.", "chunks": chunk_count}


@router.post("/rag", response_model=RAGResponse, tags=["RAG"])
async def query_rag(req: RAGRequest):
    result = await rag_service.query_rag(req.question)
    return RAGResponse(question=req.question, **result)
