import numpy as np
from fastapi import APIRouter

from app.services.document_processor import download_file, enc, parse_docx, parse_pdf

router = APIRouter()


def stats(text: str) -> dict:
    return {
        "chars": len(text),
        "words": len(text.split()),
        "tokens": len(enc.encode(text)),
        "text": text,
    }


@router.get("/health")
async def health():
    return {"status": "ok"}

@router.get("/pdf")
async def test_pdf():
    return stats(await parse_pdf("1.pdf"))

@router.get("/docx")
async def test_docx():
    return stats(await parse_docx("2.docx"))

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
    return {"similarity": similarity, "embedding": embedding, "v1": v1, "v2": v2}
