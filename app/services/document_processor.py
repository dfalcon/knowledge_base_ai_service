import os

import boto3
import pdfplumber
from botocore.config import Config
from docx import Document

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

def chunk_text(text: str, size: int = 512, overlap: int = 50) -> list[str]:
    words = text.split()
    step = size - overlap
    return [" ".join(words[i:i + size]) for i in range(0, len(words), step)]

async def process_document(data) -> str:
    pass

async def download_file(bucket, key, destination) -> None:
    s3_client.download_file(bucket, key, destination)
