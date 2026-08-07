import asyncio
from collections.abc import AsyncIterator

import asyncpg

from app.clients.db import search_fts
from app.services.document_processor import detect_language

NOTHING_FOUND = "Нічого не знайдено по вашому запиту в цій базі знань."


async def retrieve(pool: asyncpg.Pool, knowledge_base_id, question: str) -> list[asyncpg.Record]:
    async with pool.acquire() as conn:
        return await search_fts(conn, knowledge_base_id, question, detect_language(question))


async def stream_answer(rows: list[asyncpg.Record]) -> AsyncIterator[str]:
    answer = NOTHING_FOUND
    if rows:
        answer = "\n\n".join(f"{r['title']}: {' '.join(r['excerpt'].split())}" for r in rows)

    for word in answer.split(" "):
        yield word + " "
        await asyncio.sleep(0.5)  # simulate streaming delay


def build_sources(rows: list[asyncpg.Record]) -> list[dict]:
    return [
        {"document_id": str(r["id"]), "title": r["title"], "excerpt": r["excerpt"]} for r in rows
    ]
