from pydantic import BaseModel


class AutoregressiveRequest(BaseModel):
    prompt: str
    max_length: int = 128
    temperature: float = 0.8
    top_k: int = 50


class AutoregressiveResponse(BaseModel):
    prompt: str
    generated_text: str


class RAGRequest(BaseModel):
    question: str


class RAGResponse(BaseModel):
    question: str
    answer: str
    sources: list[str]
    code_examples: list[str] = []
