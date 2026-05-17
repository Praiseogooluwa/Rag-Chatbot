import os
import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from src.ingestion.loader import load_document
from src.ingestion.chunker import chunk_pages
from src.ingestion.embedder import embed_texts
from src.ingestion.vector_store import insert_document, insert_chunks, list_documents

router = APIRouter()


@router.post("/")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a PDF or TXT file.
    Pipeline: load → chunk → embed → store in Supabase
    """
    if not file.filename.endswith((".pdf", ".txt")):
        raise HTTPException(status_code=400, detail="Only PDF and TXT files are supported")

    # Save uploaded file to a temp location
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        print(f"\n=== Processing: {file.filename} ===")

        # Step 1: Load document
        pages = load_document(tmp_path)
        if not pages:
            raise HTTPException(status_code=400, detail="Could not extract text from document")

        # Step 2: Chunk
        chunks = chunk_pages(pages, chunk_size=500, chunk_overlap=50)

        # Step 3: Embed all chunks
        texts = [c["text"] for c in chunks]
        embeddings = embed_texts(texts)

        # Step 4: Store in Supabase
        document_id = insert_document(file.filename, len(chunks))
        insert_chunks(chunks, embeddings, document_id)

        return JSONResponse({
            "success": True,
            "filename": file.filename,
            "pages": len(pages),
            "chunks": len(chunks),
            "document_id": document_id,
            "message": f"Successfully processed {file.filename} into {len(chunks)} searchable chunks"
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        os.unlink(tmp_path)  # Clean up temp file


@router.get("/documents")
def get_documents():
    """List all uploaded documents."""
    try:
        docs = list_documents()
        return {"documents": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
