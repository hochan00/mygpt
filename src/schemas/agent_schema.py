from pydantic import BaseModel


class AgentRequest(BaseModel):
    message: str
    thread_id: str


class AgentResponse(BaseModel):
    message: str
