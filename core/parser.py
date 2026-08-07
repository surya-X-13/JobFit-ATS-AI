"""
core/parser.py
Resume document parsing and section segmentation.
Supports PDF (via PyMuPDF) and DOCX (via python-docx).
"""
import re
import io
from typing import Optional

# ─────────────────────────────────────────────────────────
# Section header patterns (case-insensitive regex)
# ─────────────────────────────────────────────────────────
SECTION_PATTERNS: dict[str, str] = {
    "summary": (
        r"(professional\s+summary|career\s+summary|executive\s+summary|"
        r"summary\s+of\s+qualifications?|about\s+me|profile|objective|"
        r"career\s+objective|professional\s+profile)"
    ),
    "experience": (
        r"(work\s+experience|professional\s+experience|employment(\s+history)?|"
        r"career\s+history|experience|positions?\s+held|work\s+history)"
    ),
    "education": (
        r"(education(al)?\s+(background|qualifications?)?|academic\s+background|"
        r"qualifications?|degrees?|academic\s+history|schooling)"
    ),
    "skills": (
        r"(technical\s+skills?|core\s+(competencies|skills?)|"
        r"skills?\s+(&|and)?\s+abilities|skills?|competencies|expertise|"
        r"proficiencies|areas\s+of\s+expertise)"
    ),
    "projects": (
        r"(projects?|personal\s+projects?|key\s+projects?|"
        r"notable\s+projects?|side\s+projects?|portfolio)"
    ),
    "certifications": (
        r"(certifications?|certificates?|credentials?|licenses?|"
        r"professional\s+certifications?|courses?\s+&\s+certifications?)"
    ),
    "achievements": (
        r"(achievements?|accomplishments?|honors?|awards?|"
        r"recognitions?|publications?)"
    ),
    "languages": (
        r"(languages?|spoken\s+languages?|language\s+proficiency)"
    ),
    "volunteer": (
        r"(volunteer(ing)?|community\s+service|extracurricular)"
    ),
}

# Heading line pattern — short lines (< 60 chars), all-caps or title-cased
_HEADING_RE = re.compile(
    r"^[\s]*(?:[A-Z][A-Z\s&/\-]{2,50}|[A-Z][a-z]+(?:\s+[A-Za-z&/\-]+){0,5})[\s]*$",
    re.MULTILINE,
)


def extract_text_pdf(file_bytes: bytes) -> str:
    """
    Extract text from PDF bytes using PyMuPDF (fitz).
    Returns plain text with newlines preserved.
    """
    try:
        import pymupdf as fitz  # PyMuPDF

        doc = fitz.open(stream=file_bytes, filetype="pdf")
        pages_text = []
        for page in doc:
            pages_text.append(page.get_text("text"))
        doc.close()
        return "\n".join(pages_text)
    except ImportError:
        raise ImportError("PyMuPDF not installed. Run: pip install pymupdf")
    except Exception as e:
        raise RuntimeError(f"PDF parsing failed: {e}") from e


def get_pdf_page_count(file_bytes: bytes) -> int:
    """Return the number of pages in a PDF."""
    try:
        import pymupdf as fitz

        doc = fitz.open(stream=file_bytes, filetype="pdf")
        count = len(doc)
        doc.close()
        return count
    except Exception:
        return 1


def extract_text_docx(file_bytes: bytes) -> str:
    """
    Extract text from DOCX bytes using python-docx.
    Returns plain text with newlines preserved.
    """
    try:
        from docx import Document

        doc = Document(io.BytesIO(file_bytes))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphs)
    except ImportError:
        raise ImportError("python-docx not installed. Run: pip install python-docx")
    except Exception as e:
        raise RuntimeError(f"DOCX parsing failed: {e}") from e


def extract_text(file_bytes: bytes, filename: str) -> str:
    """
    Auto-detect file type by extension and extract text.
    
    Args:
        file_bytes: Raw file bytes
        filename: Original filename (used to detect .pdf / .docx)
    Returns:
        Extracted plain text
    """
    ext = filename.lower().rsplit(".", 1)[-1]
    if ext == "pdf":
        return extract_text_pdf(file_bytes)
    elif ext in ("docx", "doc"):
        return extract_text_docx(file_bytes)
    else:
        raise ValueError(f"Unsupported file type: .{ext}. Please upload PDF or DOCX.")


def _find_section_boundaries(lines: list[str]) -> list[tuple[str, int]]:
    """
    Scan lines for section headers.
    Returns list of (section_name, line_index) tuples in order.
    """
    boundaries: list[tuple[str, int]] = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or len(stripped) > 80:
            continue
        for section, pattern in SECTION_PATTERNS.items():
            if re.fullmatch(pattern, stripped, flags=re.IGNORECASE):
                boundaries.append((section, i))
                break
    return boundaries


def segment_sections(text: str) -> dict[str, str]:
    """
    Segment resume text into named sections.
    
    Args:
        text: Full resume plain text
    Returns:
        Dict mapping section names to their content strings.
        Always includes 'full_text' key.
    """
    lines = text.splitlines()
    boundaries = _find_section_boundaries(lines)
    
    sections: dict[str, str] = {"full_text": text}

    if not boundaries:
        # No clear section headers found; return raw chunks heuristically
        sections["experience"] = text
        return sections

    # Extract content between boundaries
    for idx, (section_name, start_line) in enumerate(boundaries):
        end_line = boundaries[idx + 1][1] if idx + 1 < len(boundaries) else len(lines)
        content_lines = lines[start_line + 1 : end_line]
        content = "\n".join(content_lines).strip()
        # Merge if section appears multiple times (take first occurrence)
        if section_name not in sections:
            sections[section_name] = content

    return sections


def parse_resume(file_bytes: bytes, filename: str) -> dict:
    """
    Full pipeline: extract text → segment sections.
    
    Returns:
        {
          "full_text": str,
          "sections": dict[str, str],
          "page_count": int,
          "filename": str
        }
    """
    raw_text = extract_text(file_bytes, filename)
    sections = segment_sections(raw_text)
    
    page_count = 1
    if filename.lower().endswith(".pdf"):
        page_count = get_pdf_page_count(file_bytes)

    return {
        "full_text": raw_text,
        "sections": sections,
        "page_count": page_count,
        "filename": filename,
    }
