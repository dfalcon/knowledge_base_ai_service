import numpy as np
from fastapi import APIRouter

from app.services.document_processor import download_file, parse_docx, parse_pdf

router = APIRouter()


@router.get("/health")
async def health():
    return {"status": "ok"}

@router.get("/pdf")
async def test_pdf():
    str = await parse_pdf("1.pdf")
    return str

@router.get("/docx")
async def test_docx():
    str = await parse_docx("2.docx")
    return str

@router.get("/download")
async def test_download_file():
    await download_file("intellibase", "documents/019fc72e-5e9f-7326-bc1a-1c95f7c5c0a0/UbPK7Eqw7VXFHXBr5Hpuvr5OPkYTEpiblrZ07GHu.pdf", "tmp/destination.pdf")
    return {"status": "ok"}

@router.get("/embedding")
async def test_embedding():
    from app.services.embedding_service import get_embedding
    embedding = get_embedding("Hello, world!")
    v1, v2 = get_embedding("sick leave"), get_embedding("больничный")
    similarity = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
    return {"similarity": similarity, "embedding": embedding}
