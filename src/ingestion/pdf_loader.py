from pathlib import Path
import hashlib

import pymupdf

from src.ingestion.cleaner import clean_text


def load_pdf(file_path: str) -> list[dict]:
    """
    Extract cleaned text and metadata from a PDF, page by page.

    Args:
        file_path: Path to the PDF file.

    Returns:
        A list of dictionaries, one dictionary per page.
    """
    pdf_path = Path(file_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(f"File is not a PDF: {pdf_path}")

    document_id = hashlib.sha1(
        str(pdf_path.resolve()).encode("utf-8")
    ).hexdigest()[:12]

    document = pymupdf.open(pdf_path)

    pages = []

    for page_index, page in enumerate(document):
        raw_text = page.get_text("text")
        text = clean_text(raw_text)

        pages.append(
            {
                "document_id": document_id,
                "filename": pdf_path.name,
                "page": page_index + 1,
                "text": text,
            }
        )

    document.close()

    return pages