import re

from langchain_core.documents import Document


def format_docs(docs: list[Document]) -> str:
    if not docs:
        return "(관련 문서 없음)"
    return "\n\n---\n\n".join(doc.page_content for doc in docs)


def extract_code_blocks(text: str) -> list[str]:
    return re.findall(r"```[^\n]*\n(.*?)```", text, re.DOTALL)
