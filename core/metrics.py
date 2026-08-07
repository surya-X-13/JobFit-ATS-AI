"""
core/metrics.py
Resume quality metrics computation.
Covers: page count, word count, readability, ATS format checks.
"""
import re
from typing import Optional


def count_words(text: str) -> int:
    """Count total word tokens in text."""
    return len(text.split())


def count_sentences(text: str) -> int:
    """Rough sentence count."""
    return max(1, len(re.split(r"[.!?]+", text)))


def count_bullet_points(text: str) -> int:
    """Count lines starting with bullet characters or dash."""
    pattern = re.compile(
        r"^[\s]*[•\-\*\u2022\u2023\u25E6\u2043\u2219►▸▹▶→]\s+",
        re.MULTILINE,
    )
    return len(pattern.findall(text))


def get_readability_score(text: str) -> dict:
    """
    Compute readability metrics using textstat.
    Falls back gracefully if textstat not installed.
    """
    try:
        import textstat

        return {
            "flesch_reading_ease": round(textstat.flesch_reading_ease(text), 1),
            "flesch_kincaid_grade": round(textstat.flesch_kincaid_grade(text), 1),
            "smog_index": round(textstat.smog_index(text), 1),
            "coleman_liau_index": round(textstat.coleman_liau_index(text), 1),
            "automated_readability_index": round(
                textstat.automated_readability_index(text), 1
            ),
        }
    except (ImportError, Exception):
        # Basic approximation
        words = count_words(text)
        sentences = count_sentences(text)
        avg_words_per_sentence = words / sentences if sentences > 0 else 20
        flesch_approx = max(0, min(100, 120 - (avg_words_per_sentence * 2)))
        return {
            "flesch_reading_ease": round(flesch_approx, 1),
            "flesch_kincaid_grade": None,
            "smog_index": None,
            "coleman_liau_index": None,
            "automated_readability_index": None,
        }


def check_ats_format(text: str, filename: str = "") -> dict:
    """
    Check ATS-friendliness of resume format.
    
    Returns dict of check results and a composite score (0-100).
    """
    checks = {}
    score_contributions = []

    # 1. No tables detected (tables break ATS parsers)
    has_table_chars = bool(re.search(r"[│├┤┬┴┼─═║╔╗╚╝]", text))
    checks["no_tables"] = not has_table_chars
    score_contributions.append(15 if checks["no_tables"] else 0)

    # 2. Standard section headers present
    standard_headers = [
        r"experience|education|skills?|summary|objective",
    ]
    found_headers = any(
        re.search(p, text, re.IGNORECASE) for p in standard_headers
    )
    checks["standard_headers"] = found_headers
    score_contributions.append(15 if found_headers else 0)

    # 3. No excessive special characters
    special_ratio = len(re.findall(r"[^\w\s.,;:()\-\/+#@&%]", text)) / max(1, len(text))
    checks["minimal_special_chars"] = special_ratio < 0.02
    score_contributions.append(10 if checks["minimal_special_chars"] else 0)

    # 4. Reasonable length (200–1000 words)
    wc = count_words(text)
    checks["appropriate_length"] = 200 <= wc <= 1200
    score_contributions.append(15 if checks["appropriate_length"] else 5)

    # 5. Contains contact information
    has_email = bool(re.search(r"\b[\w.+-]+@[\w.]+\.[a-z]{2,}\b", text, re.IGNORECASE))
    checks["has_contact_info"] = has_email
    score_contributions.append(15 if has_email else 0)

    # 6. Contains action verbs (strong resume language)
    action_verbs = [
        "developed", "designed", "implemented", "managed", "led", "created",
        "built", "improved", "increased", "reduced", "achieved", "delivered",
        "launched", "streamlined", "optimized", "collaborated", "analyzed",
        "established", "coordinated", "mentored", "trained", "architected",
    ]
    found_verbs = sum(1 for v in action_verbs if re.search(rf"\b{v}\b", text, re.IGNORECASE))
    checks["action_verbs_count"] = found_verbs
    checks["strong_language"] = found_verbs >= 5
    score_contributions.append(15 if found_verbs >= 5 else (10 if found_verbs >= 2 else 0))

    # 7. Has quantified achievements (numbers in experience context)
    quantified = bool(re.search(r"\d+\s*(%|x|times|million|k\b|\+)", text, re.IGNORECASE))
    checks["quantified_achievements"] = quantified
    score_contributions.append(15 if quantified else 0)

    # 8. File format (PDF preferred)
    checks["preferred_format"] = filename.lower().endswith(".pdf")
    score_contributions.append(0)  # Informational only

    composite = min(100, sum(score_contributions))
    return {
        "checks": checks,
        "formatting_score": composite,
        "word_count": wc,
    }


def compute_metrics(text: str, page_count: int = 1, filename: str = "") -> dict:
    """
    Full metrics computation pipeline.
    
    Args:
        text: Resume plain text
        page_count: Number of pages (from PDF parser)
        filename: Original file name
    Returns:
        Comprehensive metrics dictionary
    """
    word_count = count_words(text)
    sentence_count = count_sentences(text)
    bullet_count = count_bullet_points(text)
    readability = get_readability_score(text)
    ats_format = check_ats_format(text, filename)
    avg_words_per_sentence = round(word_count / sentence_count, 1) if sentence_count > 0 else 0

    return {
        "page_count": page_count,
        "word_count": word_count,
        "sentence_count": sentence_count,
        "bullet_count": bullet_count,
        "avg_words_per_sentence": avg_words_per_sentence,
        "readability": readability,
        "ats_format": ats_format,
        "formatting_score": ats_format["formatting_score"],
    }
