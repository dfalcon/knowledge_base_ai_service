import uuid

import asyncpg
import pdfplumber
import tiktoken
from docx import Document

from app.clients.db import save_indexed
from app.clients.storage import download_file
from app.schemas.document import DocumentUploadedEvent

enc = tiktoken.encoding_for_model("text-embedding-3-small")

MIME_PDF = "application/pdf"
MIME_DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


async def parse_pdf(file_path: str) -> str:
    with pdfplumber.open(file_path) as pdf:
        # extract_text() returns None for pages without a text layer (scans, images)
        return "\n".join(page.extract_text() or "" for page in pdf.pages)

async def parse_docx(file_path: str) -> str:
    document = Document(file_path)
    return "\n".join(paragraph.text for paragraph in document.paragraphs)

def build_rows(document_id: uuid.UUID, chunks: list[str]) -> list[tuple]:
    return [
        (
            document_id,
            i,
            chunk,
            len(enc.encode(chunk)),
            uuid.uuid5(uuid.NAMESPACE_URL, f"{document_id}/{i}"),
        )
        for i, chunk in enumerate(chunks)
    ]


def chunk_text(text: str, size: int = 512, overlap: int = 50) -> list[str]:
    words = text.split()
    step = size - overlap
    return [" ".join(words[i:i + size]) for i in range(0, len(words), step)]


def detect_language(text: str) -> str:
    if set("їієґ") & set(text.lower()):
        return "ukrainian"
    if set("ыэъ") & set(text.lower()):
        return "russian"
    return "english"


async def process_document(event: DocumentUploadedEvent, pool: asyncpg.Pool) -> None:
    # Download the file from S3
    local_file_path = f"/tmp/{event.document_id}"
    await download_file(event.file_path, local_file_path)

    # Parse the document based on its type
    if event.mime_type == MIME_PDF:
        text = await parse_pdf(local_file_path)
    elif event.mime_type == MIME_DOCX:
        text = await parse_docx(local_file_path)
    else:
        raise ValueError(f"Unsupported document type: {event.mime_type}")

    # Chunk the text for further processing
    chunks = chunk_text(text)
    language = detect_language(text)

    rows = build_rows(event.document_id, chunks)
    async with pool.acquire() as conn:
        await save_indexed(conn, event.document_id, text, language, rows)
