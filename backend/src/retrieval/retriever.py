from typing import List, Dict
from src.ingestion.embedder import embed_query
from src.ingestion.vector_store import similarity_search


def retrieve(query: str, top_k: int = 5) -> List[Dict]:
    """
    Main retrieval function:
    1. Embed the user query
    2. Run similarity search in Supabase pgvector
    3. Return top-k most relevant chunks with metadata
    """
    print(f"Retrieving top {top_k} chunks for: '{query[:60]}...'")
    
    query_embedding = embed_query(query)
    results = similarity_search(query_embedding, top_k=top_k)
    
    if not results:
        print("No relevant chunks found")
        return []

    print(f"Found {len(results)} relevant chunks")
    for i, r in enumerate(results):
        print(f"  [{i+1}] {r.get('source', 'unknown')} p.{r.get('page_number', '?')} (score: {r.get('similarity', 0):.3f})")

    return results


def format_context(chunks: List[Dict]) -> str:
    """
    Format retrieved chunks into a clean context string for the LLM prompt.
    Includes source and page number so the LLM can cite them.
    """
    if not chunks:
        return "No relevant context found."

    parts = []
    for i, chunk in enumerate(chunks):
        source = chunk.get("source", "Unknown")
        page = chunk.get("page_number", "?")
        content = chunk.get("content", "")
        parts.append(f"[Source {i+1}: {source}, Page {page}]\n{content}")

    return "\n\n---\n\n".join(parts)
