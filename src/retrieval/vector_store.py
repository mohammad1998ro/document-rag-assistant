from pathlib import Path

import chromadb


class VectorStore:
    """
    Persistent vector database based on ChromaDB.
    """

    def __init__(
        self,
        persist_directory: str = "chroma_db",
        collection_name: str = "documents",
    ):
        self.persist_directory = Path(persist_directory)

        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory)
        )

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def add_chunks(
        self,
        chunks: list[dict],
        embeddings: list[list[float]],
    ) -> None:
        """
        Store chunks, embeddings, and metadata in ChromaDB.
        """
        if len(chunks) != len(embeddings):
            raise ValueError(
                "Number of chunks must match number of embeddings"
            )

        if not chunks:
            return

        ids = []
        documents = []
        metadatas = []

        for chunk in chunks:
            ids.append(chunk["chunk_id"])
            documents.append(chunk["text"])

            metadatas.append(
                {
                    "document_id": chunk["document_id"],
                    "filename": chunk["filename"],
                    "page": chunk["page"],
                    "chunk_number": chunk["chunk_number"],
                }
            )

        self.collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
    ) -> list[dict]:
        """
        Retrieve the most relevant chunks for a query embedding.
        """
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=[
                "documents",
                "metadatas",
                "distances",
            ],
        )

        retrieved = []

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        for document, metadata, distance in zip(
            documents,
            metadatas,
            distances,
        ):
            retrieved.append(
                {
                    "text": document,
                    "metadata": metadata,
                    "distance": distance,
                }
            )

        return retrieved

    def delete_document(self, document_id: str) -> None:
        """
        Delete all chunks belonging to one document.
        """
        self.collection.delete(
            where={"document_id": document_id}
        )

    def count(self) -> int:
        """
        Return the number of stored chunks.
        """
        return self.collection.count()