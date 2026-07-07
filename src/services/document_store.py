import logging

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import Language, RecursiveCharacterTextSplitter

from src.core.config import settings
from src.core.llm import embeddings

logger = logging.getLogger(__name__)


def get_vectorstore() -> Chroma:
    return Chroma(
        persist_directory=settings.CHROMA_PERSIST_DIR,
        embedding_function=embeddings,
    )


def get_retriever():
    return get_vectorstore().as_retriever(search_kwargs={"k": settings.RAG_TOP_K})


text_splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.MARKDOWN,
    chunk_size=settings.RAG_CHUNK_SIZE,
    chunk_overlap=settings.RAG_CHUNK_OVERLAP,
)


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
