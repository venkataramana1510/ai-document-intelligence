from pathlib import Path
from rag.document_loader import load_document, chunk_text
from rag.embedding_service import create_embedding
from rag.vector_store import add_document

def ingest_document(text: str, document_name: str):

    chunks = chunk_text(text, 50)

    for index, chunk in enumerate(chunks):

        embedding = create_embedding(chunk)

        chunk_id = f"{Path(document_name).stem}_chunk_{index+1}"

        metadata = {
            "source_file": document_name,
            "chunk_number": index + 1
        }

        add_document(
            chunk_id,
            chunk,
            embedding,
            metadata
        )

    return {
        "filename": Path(document_name).name,
        "chunks_created": len(chunks),
    }
    

    
