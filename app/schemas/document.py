from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class DocumentUploadedEvent(BaseModel):
    version: str
    event: str
    document_id: UUID
    knowledge_base_id: UUID
    file_path: str
    mime_type: str
    timestamp: datetime


class DocumentIndexedEvent(BaseModel):
    version: str
    event: str
    document_id: UUID
    message_id: UUID
    timestamp: datetime
