import os
from pypdf import PdfReader
from typing import List, Dict


def load_pdf(file_path: str) -> List[Dict]:
    """
    Load a PDF file and return a list of pages with text and metadata.
    Each item: { "text": str, "page": int, "source": str }
    """
    reader = PdfReader(file_path)
    pages = []

    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text and text.strip():
            pages.append({
                "text": text.strip(),
                "page": i + 1,
                "source": os.path.basename(file_path)
            })

    print(f"Loaded {len(pages)} pages from {os.path.basename(file_path)}")
    return pages


def load_text_file(file_path: str) -> List[Dict]:
    """Load a plain text file."""
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
    return [{"text": text, "page": 1, "source": os.path.basename(file_path)}]


def load_document(file_path: str) -> List[Dict]:
    """Auto-detect file type and load accordingly."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return load_pdf(file_path)
    elif ext in [".txt", ".md"]:
        return load_text_file(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}. Use PDF or TXT.")
