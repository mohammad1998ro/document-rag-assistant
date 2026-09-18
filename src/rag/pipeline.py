from src.llm.base import LLMProvider
from src.retrieval.retriever import Retriever


class RAGPipeline:
    """
    Retrieval-Augmented Generation pipeline.
    """

    def __init__(
        self,
        llm: LLMProvider,
        top_k: int = 5,
        min_similarity: float = 0.35,
    ):
        self.llm = llm
        self.retriever = Retriever(top_k=top_k)
        self.min_similarity = min_similarity

    def answer(self, question: str) -> dict:
        """
        Retrieve relevant context and generate a grounded answer.
        """
        if not question.strip():
            raise ValueError("Question cannot be empty")

        results = self.retriever.retrieve_with_scores(question)

        relevant_results = [
            result
            for result in results
            if result["similarity"] >= self.min_similarity
        ]

        if not relevant_results:
            return {
                "answer": (
                    "I could not find sufficient information in the "
                    "indexed documentation to answer this question reliably."
                ),
                "sources": [],
            }

        context_parts = []

        for i, result in enumerate(relevant_results, start=1):
            context_parts.append(
                f"[Source {i}]\n"
                f"File: {result['filename']}\n"
                f"Page: {result['page']}\n"
                f"Text:\n{result['text']}"
            )

        context = "\n\n".join(context_parts)

        prompt = f"""
You are a document-grounded assistant.

Answer the user's question using ONLY the information provided in the context.

Rules:
- Do not use outside knowledge.
- Do not invent information.
- If the context is insufficient, explicitly say that there is not enough information.
- Answer in the same language as the user's question.
- Be concise and clear.
- Do not invent citations.

Context:
{context}

Question:
{question}

Answer:
""".strip()

        answer = self.llm.generate(prompt)

        sources = []

        seen_sources = set()

        for result in relevant_results:
            source_key = (
                result["filename"],
                result["page"],
            )

            if source_key not in seen_sources:
                seen_sources.add(source_key)

                sources.append(
                    {
                        "filename": result["filename"],
                        "page": result["page"],
                        "similarity": result["similarity"],
                    }
                )

        return {
            "answer": answer,
            "sources": sources,
        }