from typing import List, Dict

SYSTEM_PROMPT = """You are a knowledgeable assistant that answers questions based strictly on the provided document context.

Rules you must follow:
1. Only use information from the context provided below
2. If the answer is not in the context, say exactly: "I don't have enough information in the uploaded documents to answer this question."
3. Always cite your sources using the format: [Source X, Page Y]
4. Be concise and direct
5. Never make up information or use outside knowledge"""


def build_prompt(query: str, context_chunks: List[Dict]) -> tuple[str, str]:
    """
    Build the final prompt to send to the LLM.
    
    Returns:
        (system_prompt, user_prompt) tuple
    """
    if not context_chunks:
        context_text = "No relevant documents found."
    else:
        parts = []
        for i, chunk in enumerate(context_chunks):
            source = chunk.get("source", "Unknown")
            page = chunk.get("page_number", "?")
            content = chunk.get("content", "")
            parts.append(f"[Source {i+1}: {source}, Page {page}]\n{content}")
        context_text = "\n\n---\n\n".join(parts)

    user_prompt = f"""CONTEXT FROM DOCUMENTS:
{context_text}

QUESTION:
{query}

Please answer the question using only the context above. Cite your sources."""

    return SYSTEM_PROMPT, user_prompt


def extract_sources(chunks: List[Dict]) -> List[Dict]:
    """Extract clean source metadata to return to the frontend."""
    sources = []
    seen = set()
    for chunk in chunks:
        key = f"{chunk.get('source')}_{chunk.get('page_number')}"
        if key not in seen:
            seen.add(key)
            sources.append({
                "source": chunk.get("source", "Unknown"),
                "page": chunk.get("page_number", 1),
                "similarity": round(chunk.get("similarity", 0), 3)
            })
    return sources
