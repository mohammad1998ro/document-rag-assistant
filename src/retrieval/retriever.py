from src.retrieval.embedder import Embedder
from src.retrieval.vector_store import VectorStore


class Retriever:
    """
    Retrieve semantically relevant chunks from the vector database.
    """

    def __init__(
        self,
        top_k: int = 5,
    ):
        if top_k <= 0:
            raise ValueError("top_k must be greater than 0")

        self.top_k = top_k
        self.embedder = Embedder()
        self.vector_store = VectorStore()

    def retrieve(self, question: str) -> list[dict]:
        """
        Retrieve the most relevant chunks for a natural-language question.
        """
        if not question.strip():
            raise ValueError("Question cannot be empty")

        query_embedding = self.embedder.embed_query(question)

        results = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=self.top_k,
        )

        return results

    def retrieve_with_scores(self, question: str) -> list[dict]:
        """
        Retrieve chunks and convert cosine distance to a similarity score.
        """
        results = self.retrieve(question)

        formatted_results = []

        for result in results:
            distance = float(result["distance"])
            similarity = 1.0 - distance

            formatted_results.append(
                {
                    "text": result["text"],
                    "filename": result["metadata"]["filename"],
                    "page": result["metadata"]["page"],
                    "document_id": result["metadata"]["document_id"],
                    "chunk_number": result["metadata"]["chunk_number"],
                    "distance": distance,
                    "similarity": similarity,
                }
            )

        return formatted_results