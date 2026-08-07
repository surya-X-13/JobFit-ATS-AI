"""
core/scorer.py
Hybrid ATS Scoring Engine.

Weights:
  Semantic Similarity    → 40%
  Skill Match            → 25%
  Experience Match       → 15%
  Education Match        → 10%
  Formatting Score       →  5%
  Keyword Density        →  5%
"""
import re
from core.embeddings import semantic_similarity_score
from core.skill_extractor import extract_skills, compute_skill_match
from core.jd_processor import process_jd
from core.metrics import compute_metrics
from core.parser import parse_resume
from utils.text_cleaner import clean_text


# ─────────────────────────────────────────────────────────
# Component weights (must sum to 1.0)
# ─────────────────────────────────────────────────────────
WEIGHTS = {
    "semantic_similarity": 0.40,
    "skill_match": 0.25,
    "experience_match": 0.15,
    "education_match": 0.10,
    "formatting_score": 0.05,
    "keyword_density": 0.05,
}


def _score_experience_match(resume_text: str, jd_data: dict, resume_sections: dict = None) -> float:
    """
    Score experience match (0-100) from text patterns.
    Extracts date ranges from experience section or full text and compares to JD requirement.
    """
    import datetime
    jd_exp = jd_data.get("experience_req", {})
    current_year = datetime.datetime.now().year

    target_text = resume_text
    if resume_sections and "experience" in resume_sections and len(resume_sections["experience"]) > 50:
        target_text = resume_sections["experience"]

    # Extract start years specifically from date ranges (e.g. 2018 - 2021, 2021 - Present)
    date_range_starts = re.findall(
        r"\b(19[789]\d|20\d{2})\b\s*[-–—to]+\s*(?:\b(?:19[789]\d|20\d{2})\b|present|current)",
        target_text,
        re.IGNORECASE,
    )
    if date_range_starts:
        start_years_int = [int(y) for y in date_range_starts if 1970 <= int(y) <= current_year]
        resume_years = current_year - min(start_years_int) if start_years_int else None
    else:
        all_years = re.findall(r"\b(19[89]\d|20\d{2})\b", target_text)
        valid_years = [int(y) for y in all_years if 1980 <= int(y) <= current_year]
        resume_years = current_year - min(valid_years) if valid_years else None

    if not jd_exp.get("found") or resume_years is None:
        return 70.0

    min_req = jd_exp.get("min_years", 0)
    if resume_years >= min_req:
        bonus = min(20.0, (resume_years - min_req) * 4)
        return min(100.0, 80.0 + bonus)
    else:
        gap = min_req - resume_years
        return max(10.0, 80.0 - (gap * 15))


DEGREE_PATTERNS = [
    (r"\b(ph\.?d|doctorate)\b", 6, "PHD"),
    (r"\b(m\.?tech|m\.?e\.?|master\s+of\s+technology)\b", 5, "MTECH"),
    (r"\b(m\.?s\.?|master\s+of\s+science|msc)\b", 5, "MS"),
    (r"\b(m\.?b\.?a\.?|master\s+of\s+business)\b", 5, "MBA"),
    (r"\b(m\.?a\.?|master\s+of\s+arts)\b", 5, "MA"),
    (r"\b(m\.?c\.?a\.?)\b", 5, "MCA"),
    (r"\b(master('?s)?\s+degree|masters?)\b", 5, "MASTER"),
    (r"\b(b\.?tech|b\.?e\.?|bachelor\s+of\s+technology|bachelor\s+of\s+engineering)\b", 4, "BTECH"),
    (r"\b(b\.?s\.?|bachelor\s+of\s+science|bsc)\b", 4, "BS"),
    (r"\b(b\.?a\.?|bachelor\s+of\s+arts)\b", 4, "BA"),
    (r"\b(b\.?c\.?a\.?)\b", 4, "BCA"),
    (r"\b(b\.?com)\b", 4, "BCOM"),
    (r"\b(bachelor('?s)?\s+degree|bachelors?)\b", 4, "BACHELOR"),
    (r"\b(associate('?s)?\s+degree)\b", 3, "ASSOCIATE"),
    (r"\bdiploma\b", 2, "DIPLOMA"),
]


def _score_education_match(resume_text: str, jd_data: dict) -> float:
    """
    Score education match (0-100) from resume text using regex word boundaries.
    Detects degree keywords accurately without false positives.
    """
    jd_edu_reqs = {r.upper() for r in jd_data.get("education_req", [])}
    if not jd_edu_reqs:
        return 75.0

    resume_text_lower = resume_text.lower()
    resume_max_level = 0
    for pattern, level, _name in DEGREE_PATTERNS:
        if re.search(pattern, resume_text_lower):
            resume_max_level = max(resume_max_level, level)

    jd_min_level = 0
    for req in jd_edu_reqs:
        req_lower = req.lower()
        for pattern, level, _name in DEGREE_PATTERNS:
            if re.search(pattern, req_lower) or _name in req:
                jd_min_level = max(jd_min_level, level)

    if jd_min_level == 0:
        return 75.0
    if resume_max_level == 0:
        return 40.0
    if resume_max_level >= jd_min_level:
        return min(100.0, 85.0 + (resume_max_level - jd_min_level) * 5)
    else:
        gap = jd_min_level - resume_max_level
        return max(20.0, 75.0 - (gap * 15))


def _score_keyword_density(resume_text: str, jd_keywords: list[str]) -> float:
    """
    Score keyword density (0-100).
    Measures how many JD keywords appear in the resume.
    """
    if not jd_keywords:
        return 50.0

    resume_lower = resume_text.lower()
    matched = sum(
        1 for kw in jd_keywords if re.search(rf"\b{re.escape(kw)}\b", resume_lower)
    )
    ratio = matched / len(jd_keywords)
    return round(min(100.0, ratio * 130), 1)


def compute_ats_score(file_bytes: bytes, filename: str, jd_text: str) -> dict:
    """
    Master scoring function. Runs the full pipeline.

    Args:
        file_bytes: Raw resume file bytes
        filename: Resume filename (.pdf or .docx)
        jd_text: Raw job description text

    Returns:
        Comprehensive score report dict
    """
    # ── Step 1: Parse resume ───────────────────────────────
    resume_data = parse_resume(file_bytes, filename)
    resume_full_text = resume_data["full_text"]
    resume_sections = resume_data["sections"]
    page_count = resume_data["page_count"]

    # ── Step 2: Extract resume skills ─────────────────────
    resume_clean = clean_text(resume_full_text)
    resume_skills_data = extract_skills(resume_clean)

    # ── Step 3: Process JD ────────────────────────────────
    jd_data = process_jd(jd_text)

    # ── Step 4: Compute metrics ───────────────────────────
    metrics = compute_metrics(resume_full_text, page_count, filename)

    # ── Step 5: Compute skill match ───────────────────────
    skill_match = compute_skill_match(
        resume_skills_data["skills_lower"],
        jd_data["skills"]["skills_lower"],
    )

    # ── Step 6: Semantic similarity ───────────────────────
    semantic_score = semantic_similarity_score(resume_clean, jd_data["clean_text"])
    semantic_score_100 = round(semantic_score * 100, 1)

    # ── Step 7: Component scores ──────────────────────────
    exp_score = _score_experience_match(resume_clean, jd_data, resume_sections)
    edu_score = _score_education_match(resume_clean, jd_data)
    kw_score = _score_keyword_density(resume_clean, jd_data["keywords"])
    format_score = float(metrics["formatting_score"])
    skill_score = skill_match["skill_score"]

    # ── Step 8: Weighted ATS score ────────────────────────
    components = {
        "semantic_similarity": semantic_score_100,
        "skill_match": skill_score,
        "experience_match": exp_score,
        "education_match": edu_score,
        "formatting_score": format_score,
        "keyword_density": kw_score,
    }

    ats_score = round(
        sum(components[k] * WEIGHTS[k] for k in WEIGHTS), 1
    )

    # ── Step 9: Assemble report ───────────────────────────
    return {
        "ats_score": ats_score,
        "components": components,
        "weights": WEIGHTS,
        "skill_match": skill_match,
        "resume_skills": resume_skills_data["skills"],
        "jd_skills": jd_data["skills"]["skills"],
        "metrics": metrics,
        "jd_data": jd_data,
        "resume_sections": resume_sections,
        "resume_full_text": resume_full_text,
        "jd_text": jd_text,
        "page_count": page_count,
        "matched_skills": skill_match["matched"],
        "missing_skills": skill_match["missing"],
        "extra_skills": skill_match["extra"],
        "score_label": _get_score_label(ats_score),
        "score_color": _get_score_color(ats_score),
    }


def _get_score_label(score: float) -> str:
    if score >= 85:
        return "Excellent Match"
    elif score >= 70:
        return "Good Match"
    elif score >= 55:
        return "Fair Match"
    elif score >= 40:
        return "Weak Match"
    else:
        return "Poor Match"


def _get_score_color(score: float) -> str:
    if score >= 85:
        return "#00e676"
    elif score >= 70:
        return "#69f0ae"
    elif score >= 55:
        return "#ffeb3b"
    elif score >= 40:
        return "#ff9800"
    else:
        return "#f44336"
