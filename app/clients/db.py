import asyncpg

INSERT_CHUNKS = """
    INSERT INTO document_chunks (document_id, chunk_index, content, tokens, qdrant_id)
    VALUES ($1, $2, $3, $4, $5)
    ON CONFLICT (document_id, chunk_index)
    DO UPDATE SET content   = EXCLUDED.content,
                  tokens    = EXCLUDED.tokens,
                  qdrant_id = EXCLUDED.qdrant_id
"""

SET_CONTENT = "UPDATE documents SET content = $2, language = $3 WHERE id = $1"

MARK_FAILED = "UPDATE documents SET status = 'failed', error_message = $2 WHERE id = $1"


async def save_indexed(
    conn: asyncpg.Connection, document_id, content: str, language: str, rows: list[tuple]
) -> None:
    async with conn.transaction():
        await conn.executemany(INSERT_CHUNKS, rows)
        await conn.execute(SET_CONTENT, document_id, content, language)


async def mark_failed(conn: asyncpg.Connection, document_id, error: str) -> None:
    await conn.execute(MARK_FAILED, document_id, error[:2000])


SEARCH_FTS = """
    WITH cfg AS (
        SELECT COALESCE(
            (SELECT cfgname::regconfig FROM pg_ts_config WHERE cfgname = $1),
            'simple'::regconfig
        ) AS c
    )
    SELECT d.id,
           d.title,
           ts_rank(d.search_vector, query)                                   AS rank,
           ts_headline(cfg.c, d.content, query,
                       'MaxWords=50, MinWords=20, StartSel="", StopSel=""')  AS excerpt
    FROM documents d, cfg, websearch_to_tsquery(cfg.c, $2) query
    WHERE d.search_vector @@ query
      AND d.knowledge_base_id = $3
      AND d.status = 'indexed'
    ORDER BY rank DESC
    LIMIT $4
"""


async def search_fts(
    conn: asyncpg.Connection,
    knowledge_base_id,
    question: str,
    language: str = "simple",
    limit: int = 5,
) -> list[asyncpg.Record]:
    """FTS half of hybrid search. The kb_id filter is required: without it results leak
    between knowledge bases.

    Misses code identifiers: the stemmer turns getDeviceStatusBy into 'getdevicestatusbi'.
    A second pass with language="simple" would find them.
    """
    return await conn.fetch(SEARCH_FTS, language, question, knowledge_base_id, limit)
