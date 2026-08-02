from pydantic import BaseModel


class ChatRequest(BaseModel):
    question: str
    knowledge_base_id: str
    conversation_id: str | None = None


class Source(BaseModel):
    document_id: str
    title: str
    excerpt: str


class ChatResponse(BaseModel):
    sources: list[Source]
