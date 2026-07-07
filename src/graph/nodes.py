from langchain_core.output_parsers import StrOutputParser

from src.core.llm import get_llm
from src.graph.state import GraphState
from src.services.document_store import get_retriever
from src.services.prompts import RAG_PROMPT
from src.services.utils import format_docs


def retrieve(state: GraphState) -> dict:
    question = state["question"]
    retriever = get_retriever()
    documents = retriever.invoke(question)
    return {"documents": documents}


def generate(state: GraphState) -> dict:
    question = state["question"]
    documents = state["documents"]

    llm = get_llm()
    chain = RAG_PROMPT | llm | StrOutputParser()
    generation = chain.invoke({"context": format_docs(documents), "question": question})
    return {"generation": generation}
