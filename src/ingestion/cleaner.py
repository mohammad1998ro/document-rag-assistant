import re


def clean_text(text: str) -> str:
    """
    Clean extracted PDF text before chunking.

    Args:
        text: Raw text extracted from a PDF page.

    Returns:
        Cleaned text.
    """

    # Replace tabs with spaces
    text = text.replace("\t", " ")

    # Normalize multiple spaces
    text = re.sub(r"[ ]{2,}", " ", text)

    # Normalize excessive line breaks
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Remove spaces at the beginning and end
    text = text.strip()

    return text