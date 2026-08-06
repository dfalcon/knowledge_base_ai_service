import asyncio
import json

from fastapi import APIRouter
from sse_starlette import EventSourceResponse

from app.schemas.chat import ChatRequest

router = APIRouter()

@router.post("/chat")
async def chat(request: ChatRequest):
    async def generate():
        for word in ["Больничный", " лист", " оформляется", " так", "."]:
            yield {"data": json.dumps({"token": word}, ensure_ascii=False)}
            await asyncio.sleep(1)

    return EventSourceResponse(generate())
