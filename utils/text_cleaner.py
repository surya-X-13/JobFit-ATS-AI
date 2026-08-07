"""
utils/text_cleaner.py
Text normalization and cleaning utilities for resume and JD text.
"""
import re
import unicodedata


def normalize_unicode(text: str) -> str:
    """Normalize unicode characters to ASCII-compatible form."""
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")


def remove_html_tags(text: str) -> str:
    """Strip HTML/XML tags from text."""
    clean = re.compile(r"<[^>]+>")
    return clean.sub(" ", text)


def remove_urls(text: str) -> str:
    """Remove URLs from text."""
    url_pattern = re.compile(
        r"https?://\S+|www\.\S+|ftp://\S+"
    )
    return url_pattern.sub(" ", text)


def remove_emails(text: str) -> str:
    """Remove email addresses from text."""
    return re.sub(r"\b[\w.%+-]+@[\w.-]+\.[A-Za-z]{2,}\b", " ", text)


def remove_phone_numbers(text: str) -> str:
    """Remove phone numbers from text."""
    return re.sub(r"(\+?\d[\d\s\-().]{7,}\d)", " ", text)


def normalize_whitespace(text: str) -> str:
    """Collapse multiple spaces/newlines into single space."""
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def remove_special_chars(text: str, keep_punctuation: bool = True) -> str:
    """Remove non-alphanumeric characters, optionally keeping punctuation."""
    if keep_punctuation:
        return re.sub(r"[^\w\s.,;:()\-\/+#@&]", " ", text)
    return re.sub(r"[^\w\s]", " ", text)


def clean_text(text: str, aggressive: bool = False) -> str:
    """
    Full cleaning pipeline.
    
    Args:
        text: Raw input text
        aggressive: If True, removes emails, phones, and URLs too
    Returns:
        Cleaned text string
    """
    text = remove_html_tags(text)
    text = normalize_unicode(text)
    text = remove_urls(text)
    if aggressive:
        text = remove_emails(text)
        text = remove_phone_numbers(text)
    text = remove_special_chars(text, keep_punctuation=True)
    text = normalize_whitespace(text)
    return text


def tokenize_sentences(text: str) -> list[str]:
    """Split text into sentences using simple rules."""
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return [s.strip() for s in sentences if len(s.strip()) > 10]


def extract_bullet_points(text: str) -> list[str]:
    """Extract lines that start with bullet-like patterns."""
    bullet_pattern = re.compile(
        r"^[\s]*[•\-\*\u2022\u2023\u25E6\u2043\u2219►▸▹▶→]\s*(.+)$",
        re.MULTILINE,
    )
    matches = bullet_pattern.findall(text)
    return [m.strip() for m in matches if len(m.strip()) > 5]
