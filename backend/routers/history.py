from fastapi import APIRouter, HTTPException
from src.ingestion.vector_store import get_session_messages

router = APIRouter()


@router.get("/{session_id}")
def get_history(session_id: str):
    """Get all messages for a chat session."""
    try:
        messages = get_session_messages(session_id)
        return {"session_id": session_id, "messages": messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
