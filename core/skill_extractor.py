"""
core/skill_extractor.py
Skill extraction pipeline.
Primary: spaCy PhraseMatcher with skill database
Optional: SkillNer (if installed)
Fallback: regex matching against skill database
"""
import re
from typing import Optional
from utils.skill_db import ALL_SKILLS, ALL_SKILLS_LOWER, SKILL_CATEGORIES


SKILL_CANONICAL_MAP: dict[str, str] = {s.lower(): s for s in ALL_SKILLS}


_spacy_nlp = None
_spacy_matcher = None


def _get_spacy_nlp_and_matcher():
    """Load and cache spaCy nlp model and PhraseMatcher singleton."""
    global _spacy_nlp, _spacy_matcher
    if _spacy_nlp is None or _spacy_matcher is None:
        import spacy
        from spacy.matcher import PhraseMatcher

        try:
            _spacy_nlp = spacy.load("en_core_web_sm")
        except Exception:
            try:
                _spacy_nlp = spacy.load("en_core_web_lg")
            except Exception:
                _spacy_nlp = spacy.blank("en")

        _spacy_matcher = PhraseMatcher(_spacy_nlp.vocab, attr="LOWER")
        patterns = [_spacy_nlp.make_doc(skill.lower()) for skill in ALL_SKILLS]
        _spacy_matcher.add("SKILLS", patterns)

    return _spacy_nlp, _spacy_matcher


def extract_skills_spacy(text: str) -> list[str]:
    """
    Extract skills using spaCy PhraseMatcher against the skill database.
    Returns deduplicated list of matched skill strings (original casing).
    """
    try:
        nlp, matcher = _get_spacy_nlp_and_matcher()
        if nlp is None or matcher is None:
            return extract_skills_regex(text)

        doc = nlp(text[:10000])  # Limit for performance
        matches = matcher(doc)

        found: set[str] = set()
        for _, start, end in matches:
            span_text = doc[start:end].text.lower()
            if span_text in SKILL_CANONICAL_MAP:
                found.add(SKILL_CANONICAL_MAP[span_text])
        return sorted(found)

    except Exception:
        return extract_skills_regex(text)


def extract_skills_skillner(text: str) -> list[str]:
    """
    Optional SkillNer extraction.
    Falls back to spaCy PhraseMatcher if SkillNer not installed.
    """
    try:
        import spacy
        from spacy.matcher import PhraseMatcher
        from skillNer.general_params import SKILL_DB
        from skillNer.skill_extractor_class import SkillExtractor

        try:
            nlp = spacy.load("en_core_web_lg")
        except Exception:
            try:
                nlp = spacy.load("en_core_web_sm")
            except Exception:
                nlp = spacy.blank("en")

        extractor = SkillExtractor(nlp, SKILL_DB, PhraseMatcher)
        annotations = extractor.annotate(text[:5000])
        
        skills = []
        for match in annotations.get("results", {}).get("full_matches", []):
            skills.append(match.get("doc_node_value", ""))
        for match in annotations.get("results", {}).get("ngram_scored", []):
            if match.get("score", 0) > 0.7:
                skills.append(match.get("doc_node_value", ""))
        
        # Supplement with our own database skills
        skills += extract_skills_spacy(text)
        return list(set(s for s in skills if s))

    except (ImportError, Exception):
        return extract_skills_spacy(text)


def extract_skills_regex(text: str) -> list[str]:
    """
    Pure regex fallback: scan text for skill database entries.
    Uses boundary matching resilient to special characters (e.g. C++, C#, .NET, CI/CD).
    """
    found: set[str] = set()
    text_lower = text.lower()
    
    for skill in ALL_SKILLS:
        skill_lower = skill.lower()
        # Non-alphanumeric boundary check to handle special chars like C++, C#, .NET, CI/CD
        pattern = r"(?<![a-zA-Z0-9])" + re.escape(skill_lower) + r"(?![a-zA-Z0-9])"
        if re.search(pattern, text_lower):
            found.add(skill)
    
    return sorted(found)


def extract_skills(text: str, use_skillner: bool = False) -> dict:
    """
    Full skill extraction pipeline.
    
    Args:
        text: Resume or JD text
        use_skillner: If True, attempt SkillNer first
    Returns:
        {
          "skills": list[str],           # All matched skills (canonical casing)
          "skills_lower": set[str],      # Lowercase set for comparison
          "by_category": dict[str, list] # Skills grouped by category
        }
    """
    if use_skillner:
        skills = extract_skills_skillner(text)
    else:
        skills = extract_skills_spacy(text)

    # Group by category
    by_category: dict[str, list[str]] = {}
    for skill in skills:
        cat = SKILL_CATEGORIES.get(skill.lower(), "Other")
        by_category.setdefault(cat, []).append(skill)

    return {
        "skills": skills,
        "skills_lower": {s.lower() for s in skills},
        "by_category": by_category,
    }


def compute_skill_match(resume_skills: set[str], jd_skills: set[str]) -> dict:
    """
    Compute skill match statistics between resume and JD.
    
    Args:
        resume_skills: Lowercase set of skills from resume
        jd_skills: Lowercase set of skills from JD
    Returns:
        {
          "matched": list[str],
          "missing": list[str],
          "extra": list[str],
          "match_ratio": float,
          "skill_score": float (0-100)
        }
    """
    if not jd_skills:
        return {
            "matched": [],
            "missing": [],
            "extra": sorted(resume_skills),
            "match_ratio": 0.0,
            "skill_score": 50.0,
        }

    matched = resume_skills & jd_skills
    missing = jd_skills - resume_skills
    extra = resume_skills - jd_skills

    ratio = len(matched) / len(jd_skills)
    skill_score = round(min(100.0, ratio * 100), 1)

    return {
        "matched": sorted(matched),
        "missing": sorted(missing),
        "extra": sorted(extra),
        "match_ratio": round(ratio, 3),
        "skill_score": skill_score,
    }
