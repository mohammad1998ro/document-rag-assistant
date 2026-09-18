import json
import unicodedata
from pathlib import Path

from src.llm.ollama_provider import OllamaProvider
from src.rag.pipeline import RAGPipeline


QUESTIONS_PATH = Path("evaluation/questions.json")


def load_questions() -> list[dict]:
    """
    Load evaluation questions from JSON.
    """
    with open(
        QUESTIONS_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def normalize_text(text: str) -> str:
    """
    Normalize text for robust keyword matching.

    This removes Romanian diacritics and converts
    text to lowercase.

    Example:
        "Clasă" -> "clasa"
        "Moștenire" -> "mostenire"
    """
    text = text.lower()

    normalized = unicodedata.normalize(
        "NFD",
        text,
    )

    without_diacritics = "".join(
        character
        for character in normalized
        if unicodedata.category(character) != "Mn"
    )

    return without_diacritics


def answer_is_rejection(answer: str) -> bool:
    """
    Detect whether the RAG system correctly refused
    to answer because the indexed documents did not
    contain enough information.
    """
    normalized = normalize_text(answer)

    rejection_phrases = [
        "not enough information",
        "could not find sufficient information",
        "cannot answer",
        "no sufficient information",
        "nu exista suficiente informatii",
        "nu am suficiente informatii",
    ]

    return any(
        phrase in normalized
        for phrase in rejection_phrases
    )


def contains_expected_keywords(
    answer: str,
    expected_keywords: list[str],
) -> bool:
    """
    Check whether all expected keywords appear
    in the generated answer after normalization.
    """
    normalized_answer = normalize_text(answer)

    normalized_keywords = [
        normalize_text(keyword)
        for keyword in expected_keywords
    ]

    return all(
        keyword in normalized_answer
        for keyword in normalized_keywords
    )


def evaluate_question(
    rag: RAGPipeline,
    item: dict,
) -> dict:
    """
    Run one evaluation question and determine
    whether the result passed.
    """
    question = item["question"]
    should_answer = item["should_answer"]

    expected_keywords = item.get(
        "expected_answer_contains",
        [],
    )

    result = rag.answer(question)

    answer = result.get(
        "answer",
        "",
    )

    sources = result.get(
        "sources",
        [],
    )

    if should_answer:

        keywords_ok = contains_expected_keywords(
            answer,
            expected_keywords,
        )

        sources_ok = bool(sources)

        passed = (
            keywords_ok
            and sources_ok
        )

        if passed:
            reason = (
                "Relevant answer with expected "
                "keywords and supporting sources."
            )

        else:
            problems = []

            if not keywords_ok:
                problems.append(
                    "missing expected keywords"
                )

            if not sources_ok:
                problems.append(
                    "no supporting sources"
                )

            reason = (
                "Expected an answer with "
                "supporting sources and keywords. "
                "Problems: "
                + ", ".join(problems)
            )

    else:

        rejection_ok = answer_is_rejection(
            answer
        )

        no_sources = not sources

        passed = (
            rejection_ok
            and no_sources
        )

        if passed:
            reason = (
                "Correctly rejected "
                "an unrelated question."
            )

        else:
            problems = []

            if not rejection_ok:
                problems.append(
                    "answer was not a clear rejection"
                )

            if not no_sources:
                problems.append(
                    "supporting sources were returned"
                )

            reason = (
                "Expected a no-answer response "
                "with no supporting sources. "
                "Problems: "
                + ", ".join(problems)
            )

    return {
        "id": item["id"],
        "question": question,
        "should_answer": should_answer,
        "answer": answer,
        "sources": sources,
        "passed": passed,
        "reason": reason,
    }


def main() -> None:
    """
    Run the complete evaluation suite.
    """

    print("=" * 70)
    print("DOCUMENT RAG ASSISTANT - EVALUATION")
    print("=" * 70)

    questions = load_questions()

    llm_provider = OllamaProvider()

    rag = RAGPipeline(
        llm_provider,
        top_k=3,
        min_similarity=0.65,
    )

    results = []

    for item in questions:

        print()
        print("-" * 70)

        print(
            f"Running {item['id']}: "
            f"{item['question']}"
        )

        try:

            result = evaluate_question(
                rag,
                item,
            )

            results.append(result)

            status = (
                "PASS"
                if result["passed"]
                else "FAIL"
            )

            print(
                f"Status: {status}"
            )

            print(
                f"Answer: {result['answer']}"
            )

            print(
                f"Sources: "
                f"{len(result['sources'])}"
            )

            print(
                f"Reason: {result['reason']}"
            )

        except Exception as exc:

            results.append(
                {
                    "id": item["id"],
                    "question": item["question"],
                    "should_answer": item[
                        "should_answer"
                    ],
                    "answer": "",
                    "sources": [],
                    "passed": False,
                    "reason": (
                        f"Evaluation error: {exc}"
                    ),
                }
            )

            print(
                "Status: ERROR"
            )

            print(
                f"Error: {exc}"
            )


    # ==================================================
    # Summary
    # ==================================================

    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    total = len(results)

    passed = sum(
        1
        for result in results
        if result["passed"]
    )

    failed = total - passed


    answerable_results = [
        result
        for result in results
        if result["should_answer"]
    ]

    rejection_results = [
        result
        for result in results
        if not result["should_answer"]
    ]


    answerable_passed = sum(
        1
        for result in answerable_results
        if result["passed"]
    )

    rejection_passed = sum(
        1
        for result in rejection_results
        if result["passed"]
    )


    accuracy = (
        passed / total
        if total
        else 0.0
    )


    print(
        f"Answerable questions: "
        f"{answerable_passed}/"
        f"{len(answerable_results)}"
    )

    print(
        f"Rejected correctly: "
        f"{rejection_passed}/"
        f"{len(rejection_results)}"
    )

    print(
        f"Overall passed: "
        f"{passed}/{total}"
    )

    print(
        f"Overall failed: "
        f"{failed}/{total}"
    )

    print(
        f"Accuracy: "
        f"{accuracy:.1%}"
    )


    # ==================================================
    # Save results
    # ==================================================

    output_path = Path(
        "evaluation/results.json"
    )

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            results,
            file,
            ensure_ascii=False,
            indent=2,
        )


    print()
    print(
        "Detailed results saved to:"
    )

    print(
        output_path
    )


if __name__ == "__main__":
    main()