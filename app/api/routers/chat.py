import json

from fastapi import APIRouter
from sse_starlette import EventSourceResponse

from app.api.deps import PoolDep
from app.schemas.chat import ChatRequest
from app.services import rag_service

router = APIRouter()


@router.post("/chat")
async def chat(request: ChatRequest, pool: PoolDep):
    rows = await rag_service.retrieve(pool, request.knowledge_base_id, request.question)

    async def generate():
        async for token in rag_service.stream_answer(rows):
            yield {"data": json.dumps({"token": token}, ensure_ascii=False)}

        yield {
            "event": "sources",
            "data": json.dumps(rag_service.build_sources(rows), ensure_ascii=False),
        }

    return EventSourceResponse(generate())
