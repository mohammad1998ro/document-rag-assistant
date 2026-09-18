from src.ingestion.pdf_loader import load_pdf
from src.ingestion.chunker import fixed_size_chunks
from src.retrieval.embedder import Embedder
from src.retrieval.vector_store import VectorStore


def index_pdf(
    file_path: str,
    chunk_size: int = 500,
    overlap: int = 100,
) -> dict:
    """
    Load, chunk, embed, and store a PDF in ChromaDB.

    Returns:
        A summary dictionary with indexing information.
    """
    pages = load_pdf(file_path)

    chunks = fixed_size_chunks(
        pages,
        chunk_size=chunk_size,
        overlap=overlap,
    )

    if not chunks:
        raise ValueError("No chunks were created from this PDF")

    texts = [chunk["text"] for chunk in chunks]

    embedder = Embedder()
    embeddings = embedder.embed_texts(texts)

    vector_store = VectorStore()
    vector_store.add_chunks(chunks, embeddings)

    return {
        "filename": chunks[0]["filename"],
        "document_id": chunks[0]["document_id"],
        "pages": len(pages),
        "chunks": len(chunks),
        "vector_store_count": vector_store.count(),
    }