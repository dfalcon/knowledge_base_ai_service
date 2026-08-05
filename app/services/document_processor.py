import os
import uuid

import asyncpg
import boto3
import pdfplumber
import tiktoken
from botocore.config import Config
from docx import Document

from app.db import save_indexed
from app.schemas.document import DocumentUploadedEvent

enc = tiktoken.encoding_for_model("text-embedding-3-small")

s3_client = boto3.client(
    "s3",
    endpoint_url=os.getenv("AWS_ENDPOINT", "http://localhost:9000"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "minioadmin"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "minioadmin"),
    region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
    config=Config(s3={"addressing_style": "path"}),
)

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

async def download_file(key, destination, bucket='intellibase',) -> None:
    s3_client.download_file(bucket, key, destination)

async def process_document(event: DocumentUploadedEvent, pool: asyncpg.Pool) -> None:
    # Download the file from S3
    local_file_path = f"tmp/{event.document_id}"
    await download_file(event.file_path, local_file_path)

    # Parse the document based on its type
    if event.mime_type == "application/pdf":
        text = await parse_pdf(local_file_path)
    elif event.mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        text = await parse_docx(local_file_path)
    else:
        raise ValueError(f"Unsupported document type: {event.mime_type}")

    # Chunk the text for further processing
    chunks = chunk_text(text)

    rows = build_rows(event.document_id, chunks)
    async with pool.acquire() as conn:
        await save_indexed(conn, event.document_id, text, rows)
