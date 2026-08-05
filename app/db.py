import asyncpg

INSERT_CHUNKS = """
    INSERT INTO document_chunks (document_id, chunk_index, content, tokens, qdrant_id)
    VALUES ($1, $2, $3, $4, $5)
    ON CONFLICT (document_id, chunk_index)
    DO UPDATE SET content   = EXCLUDED.content,
                  tokens    = EXCLUDED.tokens,
                  qdrant_id = EXCLUDED.qdrant_id
"""

SET_CONTENT = "UPDATE documents SET content = $2 WHERE id = $1"

MARK_FAILED = "UPDATE documents SET status = 'failed', error_message = $2 WHERE id = $1"


async def save_indexed(conn: asyncpg.Connection, document_id, content: str, rows: list[tuple]) -> None:
    async with conn.transaction():
        await conn.executemany(INSERT_CHUNKS, rows)
        await conn.execute(SET_CONTENT, document_id, content)


async def mark_failed(conn: asyncpg.Connection, document_id, error: str) -> None:
    await conn.execute(MARK_FAILED, document_id, error[:2000])
