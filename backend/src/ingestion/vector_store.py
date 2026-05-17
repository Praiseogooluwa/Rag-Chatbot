import os
from supabase import create_client, Client
from typing import List, Dict, Optional

def get_client() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in .env")
    return create_client(url, key)


def insert_document(document_name: str, total_chunks: int) -> str:
    """Insert a document record and return its ID."""
    client = get_client()
    result = client.table("documents").insert({
        "name": document_name,
        "total_chunks": total_chunks
    }).execute()
    return result.data[0]["id"]


def insert_chunks(chunks: List[Dict], embeddings: List[List[float]], document_id: str):
    """Insert all chunks with their embeddings into Supabase."""
    client = get_client()
    rows = []
    for chunk, embedding in zip(chunks, embeddings):
        rows.append({
            "document_id": document_id,
            "content": chunk["text"],
            "source": chunk["source"],
            "page_number": chunk["page"],
            "chunk_index": chunk["chunk_index"],
            "embedding": embedding
        })
    # Insert in batches of 100 to avoid timeouts
    for i in range(0, len(rows), 100):
        client.table("chunks").insert(rows[i:i+100]).execute()
    print(f"Inserted {len(rows)} chunks into Supabase")


def similarity_search(query_embedding: List[float], top_k: int = 5) -> List[Dict]:
    """
    Run cosine similarity search using pgvector.
    Calls the Supabase RPC function we defined in the SQL schema.
    """
    client = get_client()
    result = client.rpc("match_chunks", {
        "query_embedding": query_embedding,
        "match_count": top_k,
        "match_threshold": 0.3
    }).execute()
    return result.data


def save_message(session_id: str, role: str, content: str, sources: Optional[List[Dict]] = None):
    """Save a chat message to the messages table."""
    client = get_client()
    client.table("messages").insert({
        "session_id": session_id,
        "role": role,
        "content": content,
        "sources": sources or []
    }).execute()


def get_session_messages(session_id: str) -> List[Dict]:
    """Retrieve all messages for a chat session."""
    client = get_client()
    result = client.table("messages")\
        .select("role, content, sources, created_at")\
        .eq("session_id", session_id)\
        .order("created_at")\
        .execute()
    return result.data


def list_documents() -> List[Dict]:
    """List all uploaded documents."""
    client = get_client()
    result = client.table("documents")\
        .select("id, name, total_chunks, created_at")\
        .order("created_at", desc=True)\
        .execute()
    return result.data
