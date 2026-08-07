"""
core/rewriter.py
AI Resume Rewriter using Groq API (llama-3.3-70b-versatile).
Transforms unstructured resume text into a high-impact, ATS-optimized JSON resume model.
"""
import os
import json
import re
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


def _get_groq_client():
    """Initialize and return a Groq client."""
    try:
        from groq import Groq
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not set in environment.")
        return Groq(api_key=GROQ_API_KEY)
    except ImportError:
        raise ImportError("groq package not installed.")


REWRITE_PROMPT_TEMPLATE = """
You are an elite ATS resume strategist and professional resume writer.

## Candidate Original Resume:
{resume_text}

## Target Job Description:
{jd_text}

## ATS Skill Gap Analysis:
- Matched Skills: {matched_skills}
- Missing Skills to Incorporate: {missing_skills}

## Task:
Rewrite and structure the candidate's resume to maximize ATS match percentage and executive impact.
Integrate the missing skills seamlessly into relevant experience bullet points and the technical skills matrix.

Return ONLY a valid JSON object matching this EXACT schema (no markdown formatting outside JSON):

{{
  "full_name": "Candidate Full Name (or 'CANDIDATE NAME' if unstated)",
  "contact_info": "email | phone | location | linkedin",
  "professional_summary": "A powerful 3-4 sentence professional summary aligning candidate experience directly with target JD requirements.",
  "technical_skills": {{
    "Languages & Frameworks": ["Skill1", "Skill2"],
    "Cloud & Infrastructure": ["Skill3", "Skill4"],
    "Databases & Tools": ["Skill5", "Skill6"]
  }},
  "work_experience": [
    {{
      "title": "Job Title",
      "company": "Company Name",
      "location_dates": "City, State | Year – Year",
      "bullet_points": [
        "High-impact bullet point starting with a strong action verb, incorporating metrics and relevant skills.",
        "Second quantified achievement bullet point.",
        "Third bullet point demonstrating technical execution."
      ]
    }}
  ],
  "education": [
    {{
      "degree": "Degree Name (e.g. Bachelor of Science in Computer Science)",
      "institution_dates": "University Name | Year – Year"
    }}
  ],
  "projects": [
    {{
      "name": "Project Name",
      "details": "Description of project architecture, stack used, and key outcomes."
    }}
  ]
}}
""".strip()


def rewrite_resume_with_ai(
    resume_text: str,
    jd_text: str,
    score_report: dict,
) -> dict:
    """
    Rewrite unstructured resume text into a structured, ATS-optimized JSON resume data structure.
    """
    matched = ", ".join(score_report.get("matched_skills", [])) or "None"
    missing = ", ".join(score_report.get("missing_skills", [])) or "None"

    if not GROQ_API_KEY:
        return _fallback_rewritten_resume(resume_text, score_report)

    prompt = REWRITE_PROMPT_TEMPLATE.format(
        resume_text=resume_text[:3500],
        jd_text=jd_text[:2500],
        matched_skills=matched,
        missing_skills=missing,
    )

    try:
        client = _get_groq_client()
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert resume writer. Respond ONLY with valid JSON, no markdown block fences.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
            max_tokens=2500,
        )

        content = response.choices[0].message.content.strip()
        content = re.sub(r"^```(?:json)?\s*", "", content)
        content = re.sub(r"\s*```$", "", content)

        data = json.loads(content)
        data["_source"] = "groq"
        return data

    except (json.JSONDecodeError, Exception) as e:
        return _fallback_rewritten_resume(resume_text, score_report, error=str(e))


def _fallback_rewritten_resume(resume_text: str, score_report: dict, error: str = "") -> dict:
    """Rule-based fallback resume model when Groq API is offline."""
    matched = score_report.get("matched_skills", [])
    missing = score_report.get("missing_skills", [])
    all_skills = list(set([s.title() for s in matched + missing])) or ["Python", "SQL", "Docker", "AWS", "REST API"]

    return {
        "full_name": "CANDIDATE NAME",
        "contact_info": "candidate@email.com | (555) 019-2834 | New York, NY | linkedin.com/in/candidate",
        "professional_summary": (
            "Results-driven Senior Engineer with extensive experience developing scalable cloud architectures, "
            "high-performance microservices, and automated data processing pipelines. Proven track record of optimizing "
            "system throughput, reducing API latency, and deploying robust production software."
        ),
        "technical_skills": {
            "Core Technologies": all_skills[:6],
            "Cloud & Infrastructure": ["Docker", "Kubernetes", "AWS", "Terraform", "CI/CD"],
            "Databases & Tools": ["PostgreSQL", "Redis", "MongoDB", "Git", "REST API"],
        },
        "work_experience": [
            {
                "title": "Senior Software Engineer",
                "company": "Technology Solutions Inc.",
                "location_dates": "New York, NY | 2021 – Present",
                "bullet_points": [
                    "Engineered microservices architecture using Python and FastAPI, increasing system throughput by 40%.",
                    "Architected and managed containerized deployments on AWS EKS with Kubernetes, achieving 99.99% uptime.",
                    f"Integrated core technical competencies including {', '.join(all_skills[:3])} to optimize workflow performance.",
                ],
            },
            {
                "title": "Software Engineer",
                "company": "Enterprise Data Systems",
                "location_dates": "New York, NY | 2018 – 2021",
                "bullet_points": [
                    "Developed web applications and REST APIs serving over 100k active users.",
                    "Built automated CI/CD pipelines with GitHub Actions, reducing deployment cycle times by 50%.",
                ],
            },
        ],
        "education": [
            {
                "degree": "Bachelor of Science in Computer Science",
                "institution_dates": "State University | 2014 – 2018",
            }
        ],
        "projects": [
            {
                "name": "High-Concurrency Data Pipeline",
                "details": "Engineered real-time data streaming pipeline handling 10,000 req/sec using Python, Kafka, and Redis.",
            }
        ],
        "_source": "fallback",
        "_error": error,
    }
