"""
core/jd_processor.py
Job Description text processing:
- Clean and normalize JD text
- Extract required skills and keywords
- Extract seniority level and experience requirements
"""
import re
from utils.text_cleaner import clean_text, remove_html_tags
from core.skill_extractor import extract_skills


# ─────────────────────────────────────────────────────────
# Seniority level detection
# ─────────────────────────────────────────────────────────
SENIORITY_PATTERNS = {
    "intern": r"\b(intern(ship)?|co-op|trainee)\b",
    "junior": r"\b(junior|jr\.?|entry[- ]level|0[- ]?[to\-]?[123][+]?\s+year)\b",
    "mid": r"\b(mid[- ]level|intermediate|[2-4]\+?\s+years?)\b",
    "senior": r"\b(senior|sr\.?|lead|principal|[5-9]\+?\s+years?|10\+?\s+years?)\b",
    "manager": r"\b(manager|management|director|head\s+of|vp|vice\s+president)\b",
}

EXP_PATTERNS = [
    # 3 - 5 years of experience / 3 to 5 years experience
    re.compile(r"(\d+)\s*(?:to|-)\s*(\d+)\s*years?\s+(?:of\s+)?(?:[\w\s]{0,30}\s+)?(?:experience|exp)", re.IGNORECASE),
    # 5+ years of experience / 5+ years exp
    re.compile(r"(\d+)\+\s*years?\s+(?:of\s+)?(?:[\w\s]{0,30}\s+)?(?:experience|exp)", re.IGNORECASE),
    # minimum / at least 5 years of experience
    re.compile(r"(?:minimum|at\s+least|min\.?)\s+(\d+)\s*years?\s+(?:of\s+)?(?:[\w\s]{0,30}\s+)?(?:experience|exp)", re.IGNORECASE),
    # 5 years of experience
    re.compile(r"(\d+)\s*years?\s+(?:of\s+)?(?:[\w\s]{0,30}\s+)?(?:experience|exp)", re.IGNORECASE),
]

EDUCATION_REQ_RE = re.compile(
    r"\b(bachelor|master|phd|doctorate|B\.?S\.?|M\.?S\.?|B\.?E\.?|M\.?E\.?|"
    r"B\.?Tech|M\.?Tech|MBA|degree)\b",
    re.IGNORECASE,
)


def extract_experience_requirement(text: str) -> dict:
    """Extract years of experience required from JD."""
    for pattern in EXP_PATTERNS:
        match = pattern.search(text)
        if match:
            groups = match.groups()
            try:
                min_years = int(groups[0])
                if len(groups) > 1 and groups[1] is not None:
                    max_years = int(groups[1])
                else:
                    max_years = min_years + 3
                return {"min_years": min_years, "max_years": max_years, "found": True}
            except ValueError:
                continue
    return {"min_years": 0, "max_years": 0, "found": False}


def detect_seniority(text: str) -> str:
    """Detect the seniority level targeted by the JD."""
    text_lower = text.lower()
    for level, pattern in SENIORITY_PATTERNS.items():
        if re.search(pattern, text_lower):
            return level
    return "mid"  # default


def extract_education_requirement(text: str) -> list[str]:
    """Extract required education levels from JD."""
    matches = EDUCATION_REQ_RE.findall(text)
    return list(set(m.upper() for m in matches))


def extract_keywords(text: str, top_n: int = 50) -> list[str]:
    """
    Extract important non-stop-word keywords from JD using TF-like scoring.
    Returns top N keywords by frequency.
    """
    # Minimal stopwords
    STOPWORDS = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "up", "about", "into", "through", "during",
        "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
        "do", "does", "did", "will", "would", "could", "should", "may", "might",
        "shall", "can", "need", "we", "you", "they", "it", "he", "she", "our",
        "your", "their", "this", "that", "these", "those", "which", "who", "what",
        "as", "if", "than", "then", "so", "yet", "both", "either", "neither",
        "not", "no", "nor", "only", "own", "same", "than", "too", "very",
        "must", "such", "well", "also", "just", "over", "under", "work",
    }
    
    words = re.findall(r"\b[a-zA-Z][a-zA-Z\+\#\.]{2,}\b", text)
    freq: dict[str, int] = {}
    for word in words:
        word_l = word.lower()
        if word_l not in STOPWORDS and len(word_l) > 2:
            freq[word_l] = freq.get(word_l, 0) + 1

    # Sort by frequency and return top N
    sorted_keywords = sorted(freq.items(), key=lambda x: -x[1])
    return [kw for kw, _ in sorted_keywords[:top_n]]


def process_jd(jd_text: str) -> dict:
    """
    Full JD processing pipeline.
    
    Args:
        jd_text: Raw job description text
    Returns:
        {
          "clean_text": str,
          "skills": dict,              # From extract_skills()
          "keywords": list[str],
          "experience_req": dict,
          "education_req": list[str],
          "seniority": str,
        }
    """
    # Step 1: Clean text
    clean = clean_text(remove_html_tags(jd_text))

    # Step 2: Extract skills
    skills_data = extract_skills(clean)

    # Step 3: Extract keywords
    keywords = extract_keywords(clean)

    # Step 4: Extract requirements
    experience_req = extract_experience_requirement(clean)
    education_req = extract_education_requirement(clean)
    seniority = detect_seniority(clean)

    return {
        "clean_text": clean,
        "skills": skills_data,
        "keywords": keywords,
        "experience_req": experience_req,
        "education_req": education_req,
        "seniority": seniority,
    }
