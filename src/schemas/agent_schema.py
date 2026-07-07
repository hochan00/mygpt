from pydantic import BaseModel


class AgentRequest(BaseModel):
    question: str


class AgentResponse(BaseModel):
    question: str
    answer: str
    sources: list[str]
    code_examples: list[str] = []
