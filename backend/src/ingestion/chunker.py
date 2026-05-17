from typing import List, Dict
from langchain.text_splitter import RecursiveCharacterTextSplitter


def chunk_pages(pages: List[Dict], chunk_size: int = 500, chunk_overlap: int = 50) -> List[Dict]:
    """
    Split page texts into overlapping chunks for better retrieval.
    
    Args:
        pages: List of page dicts from loader.py
        chunk_size: Max characters per chunk (500 is a good default)
        chunk_overlap: Characters to overlap between chunks (helps context continuity)
    
    Returns:
        List of chunk dicts with text, source, page, and chunk_index
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    chunks = []
    chunk_index = 0

    for page in pages:
        page_chunks = splitter.split_text(page["text"])
        for chunk_text in page_chunks:
            if chunk_text.strip():
                chunks.append({
                    "text": chunk_text.strip(),
                    "source": page["source"],
                    "page": page["page"],
                    "chunk_index": chunk_index
                })
                chunk_index += 1

    print(f"Created {len(chunks)} chunks from {len(pages)} pages")
    return chunks
