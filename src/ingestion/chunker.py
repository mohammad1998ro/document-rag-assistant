def fixed_size_chunks(
    pages: list[dict],
    chunk_size: int = 500,
    overlap: int = 100,
) -> list[dict]:
    """
    Split page text into fixed-size character chunks while preserving metadata.

    Args:
        pages: Output of load_pdf(), one dictionary per page.
        chunk_size: Number of characters per chunk.
        overlap: Number of overlapping characters between consecutive chunks.

    Returns:
        A list of chunk dictionaries.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")

    if overlap < 0:
        raise ValueError("overlap cannot be negative")

    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    chunks = []

    for page in pages:
        text = page["text"]

        if not text:
            continue

        start = 0
        chunk_number = 1

        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end].strip()

            if chunk_text:
                chunk_id = (
                    f"{page['document_id']}_"
                    f"{page['page']:04d}_"
                    f"{chunk_number:03d}"
                )

                chunks.append(
                    {
                        "document_id": page["document_id"],
                        "filename": page["filename"],
                        "page": page["page"],
                        "chunk_number": chunk_number,
                        "chunk_id": chunk_id,
                        "text": chunk_text,
                    }
                )

                chunk_number += 1

            start += chunk_size - overlap

    return chunks


def paragraph_aware_chunks(
    pages: list[dict],
    max_chunk_size: int = 1000,
) -> list[dict]:
    """
    Create chunks while trying to preserve paragraph boundaries.

    Args:
        pages: Output of load_pdf(), one dictionary per page.
        max_chunk_size: Maximum approximate number of characters per chunk.

    Returns:
        A list of chunk dictionaries.
    """
    if max_chunk_size <= 0:
        raise ValueError("max_chunk_size must be greater than 0")

    chunks = []

    for page in pages:
        text = page["text"]

        if not text:
            continue

        paragraphs = [
            paragraph.strip()
            for paragraph in text.split("\n\n")
            if paragraph.strip()
        ]

        current_chunk = ""
        chunk_number = 1

        for paragraph in paragraphs:
            candidate = (
                f"{current_chunk}\n\n{paragraph}".strip()
                if current_chunk
                else paragraph
            )

            if len(candidate) <= max_chunk_size:
                current_chunk = candidate
            else:
                if current_chunk:
                    chunk_id = (
                        f"{page['document_id']}_"
                        f"{page['page']:04d}_"
                        f"{chunk_number:03d}"
                    )

                    chunks.append(
                        {
                            "document_id": page["document_id"],
                            "filename": page["filename"],
                            "page": page["page"],
                            "chunk_number": chunk_number,
                            "chunk_id": chunk_id,
                            "text": current_chunk,
                        }
                    )

                    chunk_number += 1

                current_chunk = paragraph

        if current_chunk:
            chunk_id = (
                f"{page['document_id']}_"
                f"{page['page']:04d}_"
                f"{chunk_number:03d}"
            )

            chunks.append(
                {
                    "document_id": page["document_id"],
                    "filename": page["filename"],
                    "page": page["page"],
                    "chunk_number": chunk_number,
                    "chunk_id": chunk_id,
                    "text": current_chunk,
                }
            )

    return chunks