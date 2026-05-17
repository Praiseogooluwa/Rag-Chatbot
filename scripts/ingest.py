"""
Ingest Script
=============
Processes all PDF/TXT files in data/raw/ and stores them in Supabase.
Run this after scraping or manually adding documents.

Usage:
    cd backend
    python ../scripts/ingest.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/backend")

from pathlib import Path
from dotenv import load_dotenv

load_dotenv("backend/.env")

from src.ingestion.loader import load_document
from src.ingestion.chunker import chunk_pages
from src.ingestion.embedder import embed_texts
from src.ingestion.vector_store import insert_document, insert_chunks

DATA_DIR = Path("data/raw")


def ingest_all():
    files = list(DATA_DIR.glob("*.pdf")) + list(DATA_DIR.glob("*.txt"))
    if not files:
        print(f"No PDF or TXT files found in {DATA_DIR}")
        print("Run scripts/scrape_cbn.py first or manually add PDFs to data/raw/")
        return

    print(f"\n=== Ingesting {len(files)} documents ===\n")
    total_chunks = 0

    for file_path in files:
        print(f"Processing: {file_path.name}")
        try:
            pages = load_document(str(file_path))
            chunks = chunk_pages(pages)
            texts = [c["text"] for c in chunks]
            embeddings = embed_texts(texts)
            doc_id = insert_document(file_path.name, len(chunks))
            insert_chunks(chunks, embeddings, doc_id)
            total_chunks += len(chunks)
            print(f"  ✅ Done: {len(chunks)} chunks\n")
        except Exception as e:
            print(f"  ❌ Failed: {e}\n")

    print(f"=== Ingestion complete: {total_chunks} total chunks stored in Supabase ===")


if __name__ == "__main__":
    ingest_all()
