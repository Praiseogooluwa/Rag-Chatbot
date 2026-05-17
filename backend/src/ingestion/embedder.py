import os
from typing import List
import google.generativeai as genai
from sentence_transformers import SentenceTransformer

# Load once at module level (avoids reloading on every call)
_local_model = None

def _get_local_model():
    global _local_model
    if _local_model is None:
        print("Loading local embedding model (first time only, ~80MB)...")
        _local_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _local_model


def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Embed a list of texts into vectors.
    Uses GEMINI_API_KEY if set (768 dimensions), otherwise falls back to local model (384 dimensions).
    
    Returns list of float vectors, one per input text.
    """
    model_choice = os.getenv("EMBEDDING_MODEL", "local")

    if model_choice == "gemini" and os.getenv("GEMINI_API_KEY"):
        return _embed_with_gemini(texts)
    else:
        return _embed_with_local(texts)


def _embed_with_gemini(texts: List[str]) -> List[List[float]]:
    """Use Google's text-embedding-004 model — free tier: 1500 requests/day."""
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    embeddings = []
    # Gemini embeds one at a time
    for text in texts:
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=text,
            task_type="retrieval_document"
        )
        embeddings.append(result["embedding"])
    print(f"Embedded {len(texts)} texts with Gemini")
    return embeddings


def _embed_with_local(texts: List[str]) -> List[List[float]]:
    """Use sentence-transformers locally — completely free, no API needed."""
    model = _get_local_model()
    vectors = model.encode(texts, show_progress_bar=False)
    return [v.tolist() for v in vectors]


def embed_query(query: str) -> List[float]:
    """Embed a single query string for similarity search."""
    model_choice = os.getenv("EMBEDDING_MODEL", "local")

    if model_choice == "gemini" and os.getenv("GEMINI_API_KEY"):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=query,
            task_type="retrieval_query"
        )
        return result["embedding"]
    else:
        model = _get_local_model()
        return model.encode(query).tolist()
