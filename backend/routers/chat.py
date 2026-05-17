import json
import uuid
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional

from src.retrieval.retriever import retrieve
from src.generation.prompt_builder import build_prompt, extract_sources
from src.generation.llm import stream_llm
from src.ingestion.vector_store import save_message

router = APIRouter()


class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    top_k: Optional[int] = 5


@router.post("/")
async def chat(request: ChatRequest):
    """
    Main chat endpoint with streaming response.
    Pipeline: retrieve → build prompt → stream LLM → save to DB
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    session_id = request.session_id or str(uuid.uuid4())

    # Step 1: Retrieve relevant chunks
    chunks = retrieve(request.query, top_k=request.top_k)
    sources = extract_sources(chunks)

    # Step 2: Build prompt
    system_prompt, user_prompt = build_prompt(request.query, chunks)

    # Step 3: Save user message
    save_message(session_id, "user", request.query)

    # Step 4: Stream response
    async def generate():
        full_response = ""

        # First yield the sources as metadata
        yield f"data: {json.dumps({'type': 'sources', 'sources': sources, 'session_id': session_id})}\n\n"

        # Then stream the actual text
        for token in stream_llm(user_prompt, system_prompt):
            full_response += token
            yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"

        # Signal completion
        yield f"data: {json.dumps({'type': 'done'})}\n\n"

        # Save assistant response to DB
        save_message(session_id, "assistant", full_response, sources)

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )
