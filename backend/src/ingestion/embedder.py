import os
import time
from typing import List
import google.generativeai as genai


def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Embed texts using Gemini gemini-embedding-001.
    Rate limit: 100 requests/minute on free tier.
    We add a small delay between requests to avoid hitting the limit.
    """
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    embeddings = []
    for i, text in enumerate(texts):
        # Rate limit protection — sleep every 80 requests
        if i > 0 and i % 80 == 0:
            print(f"  Rate limit pause at chunk {i}/{len(texts)} — waiting 65 seconds...")
            time.sleep(65)
        try:
            result = genai.embed_content(
                model="models/gemini-embedding-001",
                content=text,
                task_type="retrieval_document",
                output_dimensionality=768
            )
            embeddings.append(result["embedding"])
        except Exception as e:
            if "429" in str(e):
                print(f"  Rate limit hit at chunk {i} — waiting 65 seconds...")
                time.sleep(65)
                # Retry once
                result = genai.embed_content(
                    model="models/gemini-embedding-001",
                    content=text,
                    task_type="retrieval_document",
                    output_dimensionality=768
                )
                embeddings.append(result["embedding"])
            else:
                raise e

    print(f"Embedded {len(texts)} texts with Gemini")
    return embeddings


def embed_query(query: str) -> List[float]:
    """Embed a single query string for similarity search."""
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    result = genai.embed_content(
        model="models/gemini-embedding-001",
        content=query,
        task_type="retrieval_query",
        output_dimensionality=768
    )
    return result["embedding"]