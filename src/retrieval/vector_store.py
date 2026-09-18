from pathlib import Path

import chromadb


class VectorStore:
    """
    Persistent ChromaDB vector store for RAG document chunks.
    """

    def __init__(
        self,
        persist_directory: str = "chroma_db",
        collection_name: str = "documents",
    ):
        """
        Initialize the persistent ChromaDB collection.
        """

        self.persist_directory = str(
            Path(persist_directory)
        )

        self.client = chromadb.PersistentClient(
            path=self.persist_directory
        )

        self.collection = (
            self.client.get_or_create_collection(
                name=collection_name,
                metadata={
                    "hnsw:space": "cosine"
                },
            )
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
                "Number of chunks must match "
                "number of embeddings"
            )

        if not chunks:
            return

        ids = []
        documents = []
        metadatas = []

        for chunk in chunks:

            ids.append(
                chunk["chunk_id"]
            )

            documents.append(
                chunk["text"]
            )

            metadatas.append(
                {
                    "document_id": chunk[
                        "document_id"
                    ],
                    "filename": chunk[
                        "filename"
                    ],
                    "page": chunk[
                        "page"
                    ],
                    "chunk_number": chunk[
                        "chunk_number"
                    ],
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
        Retrieve the most relevant chunks
        for a query embedding.
        """

        if self.count() == 0:
            return []

        top_k = min(
            top_k,
            self.count(),
        )

        results = self.collection.query(
            query_embeddings=[
                query_embedding
            ],
            n_results=top_k,
            include=[
                "documents",
                "metadatas",
                "distances",
            ],
        )

        retrieved = []

        documents = (
            results["documents"][0]
            if results.get("documents")
            else []
        )

        metadatas = (
            results["metadatas"][0]
            if results.get("metadatas")
            else []
        )

        distances = (
            results["distances"][0]
            if results.get("distances")
            else []
        )

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

    def get_document_ids_by_filename(
        self,
        filename: str,
    ) -> list[str]:
        """
        Return all unique document IDs
        associated with a filename.
        """

        results = self.collection.get(
            where={
                "filename": filename
            },
            include=[
                "metadatas"
            ],
        )

        document_ids = set()

        for metadata in results.get(
            "metadatas",
            [],
        ):
            if (
                metadata
                and metadata.get(
                    "document_id"
                )
            ):
                document_ids.add(
                    metadata[
                        "document_id"
                    ]
                )

        return sorted(
            document_ids
        )

    def delete_document(
        self,
        document_id: str,
    ) -> None:
        """
        Delete all chunks belonging
        to one document.
        """

        self.collection.delete(
            where={
                "document_id":
                document_id
            }
        )

    def delete_document_by_filename(
        self,
        filename: str,
    ) -> int:
        """
        Delete every indexed document
        associated with a filename.

        Returns the number of document IDs
        that were removed.
        """

        document_ids = (
            self.get_document_ids_by_filename(
                filename
            )
        )

        for document_id in document_ids:
            self.delete_document(
                document_id
            )

        return len(
            document_ids
        )

    def count(self) -> int:
        """
        Return the number
        of stored chunks.
        """

        return self.collection.count()