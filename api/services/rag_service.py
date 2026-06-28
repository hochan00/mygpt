import logging
from typing import Any

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, load_prompt
from langchain_core.runnables import RunnablePassthrough
from langchain_text_splitters import RecursiveCharacterTextSplitter

from api.core.config import settings
from api.core.llm import embeddings, get_llm

logger = logging.getLogger(__name__)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=settings.RAG_CHUNK_SIZE,
    chunk_overlap=settings.RAG_CHUNK_OVERLAP,
)

rag_yaml = load_prompt("api/prompts/rag.yaml", encoding="utf-8")
RAG_PROMPT = ChatPromptTemplate.from_messages(
    [("human", rag_yaml.template)]
)


def _get_vectorstore() -> Chroma:
    return Chroma(
        persist_directory=settings.CHROMA_PERSIST_DIR,
        embedding_function=embeddings,
    )


def format_docs(docs: list[Document]) -> str:
    if not docs:
        return "(관련 문서 없음)"
    return "\n\n---\n\n".join(doc.page_content for doc in docs)


async def add_documents(text: str, source: str) -> int:
    documents = [Document(page_content=text, metadata={"source": source})]
    chunks = text_splitter.split_documents(documents)
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=settings.CHROMA_PERSIST_DIR,
    )
    count = vectorstore._collection.count()
    logger.info("문서 '%s' 등록 완료: %d 청크", source, count)
    return count


async def query_rag(question: str) -> dict[str, Any]:
    llm = get_llm()
    retriever = _get_vectorstore().as_retriever(
        search_kwargs={"k": settings.RAG_TOP_K}
    )

    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | RAG_PROMPT
        | llm
        | StrOutputParser()
    )

    answer = chain.invoke(question)

    docs = retriever.invoke(question)
    sources = list({doc.metadata.get("source", "") for doc in docs})

    return {"answer": answer, "sources": sources}
