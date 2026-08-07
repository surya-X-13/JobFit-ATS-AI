"""
core/feedback.py
AI Feedback Generator using Groq API (llama-3.3-70b-versatile).
Produces structured, actionable resume improvement suggestions.
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
        raise ImportError("groq package not installed. Run: pip install groq")


FEEDBACK_PROMPT_TEMPLATE = """
You are an expert ATS (Applicant Tracking System) career coach and resume specialist.

## Resume (First 3000 chars):
{resume_text}

## Job Description (First 2000 chars):
{jd_text}

## ATS Score Report:
- Overall ATS Score: {ats_score}/100
- Semantic Match: {semantic_score}%
- Skill Match Score: {skill_score}%
- Missing Skills: {missing_skills}
- Matched Skills: {matched_skills}
- Word Count: {word_count}
- Formatting Score: {formatting_score}/100

## Your Task:
Analyze the resume against the job description and ATS score report. 
Return a JSON object with EXACTLY this structure (no extra text, just valid JSON):

{{
  "overall_assessment": "2-3 sentence summary of how well the resume matches",
  "strengths": [
    "strength 1",
    "strength 2",
    "strength 3"
  ],
  "missing_skills_analysis": [
    {{
      "skill": "skill name",
      "importance": "critical|high|medium",
      "suggestion": "how to add or demonstrate this skill"
    }}
  ],
  "bullet_point_improvements": [
    {{
      "original": "original bullet (or describe the gap)",
      "improved": "improved version with metrics and action verbs"
    }}
  ],
  "ats_optimization_tips": [
    "tip 1",
    "tip 2",
    "tip 3",
    "tip 4"
  ],
  "keyword_suggestions": [
    "keyword1",
    "keyword2",
    "keyword3",
    "keyword4",
    "keyword5"
  ],
  "priority_actions": [
    {{
      "action": "action description",
      "impact": "high|medium|low",
      "effort": "high|medium|low"
    }}
  ]
}}

Be specific, actionable, and professional. Focus on ATS optimization strategies.
""".strip()


def generate_feedback(
    resume_text: str,
    jd_text: str,
    score_report: dict,
) -> dict:
    """
    Generate structured AI feedback using Groq.
    
    Args:
        resume_text: Full resume plain text
        jd_text: Job description text
        score_report: Output from scorer.compute_ats_score()
    
    Returns:
        Parsed feedback dict, or fallback dict if API fails.
    """
    if not GROQ_API_KEY:
        return _fallback_feedback(score_report)

    prompt = FEEDBACK_PROMPT_TEMPLATE.format(
        resume_text=resume_text[:3000],
        jd_text=jd_text[:2000],
        ats_score=score_report.get("ats_score", 0),
        semantic_score=round(score_report.get("components", {}).get("semantic_similarity", 0), 1),
        skill_score=round(score_report.get("components", {}).get("skill_match", 0), 1),
        missing_skills=", ".join(score_report.get("missing_skills", [])[:10]) or "None identified",
        matched_skills=", ".join(score_report.get("matched_skills", [])[:10]) or "None identified",
        word_count=score_report.get("metrics", {}).get("word_count", "N/A"),
        formatting_score=round(score_report.get("components", {}).get("formatting_score", 0), 1),
    )

    try:
        client = _get_groq_client()
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert ATS resume coach. "
                        "Always respond with valid JSON only, no markdown code blocks."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
            max_tokens=2048,
        )

        content = response.choices[0].message.content.strip()

        # Strip markdown code fences if present
        content = re.sub(r"^```(?:json)?\s*", "", content)
        content = re.sub(r"\s*```$", "", content)

        feedback = json.loads(content)
        feedback["_source"] = "groq"
        return feedback

    except json.JSONDecodeError:
        # Try to extract JSON from response
        try:
            json_match = re.search(r"\{.*\}", content, re.DOTALL)
            if json_match:
                feedback = json.loads(json_match.group())
                feedback["_source"] = "groq"
                return feedback
        except Exception:
            pass
        return _fallback_feedback(score_report, error="JSON parse failed")

    except Exception as e:
        return _fallback_feedback(score_report, error=str(e))


def _fallback_feedback(score_report: dict, error: str = "") -> dict:
    """
    Rule-based fallback feedback when Groq API is unavailable.
    """
    ats_score = score_report.get("ats_score", 0)
    missing = score_report.get("missing_skills", [])
    matched = score_report.get("matched_skills", [])
    word_count = score_report.get("metrics", {}).get("word_count", 0)

    strengths = []
    if matched:
        strengths.append(f"Strong skill alignment: {', '.join(matched[:5])}")
    if word_count >= 300:
        strengths.append("Resume has adequate content length")
    if score_report.get("components", {}).get("formatting_score", 0) >= 70:
        strengths.append("Good ATS-friendly formatting detected")
    if not strengths:
        strengths = ["Resume submitted for analysis"]

    missing_analysis = [
        {
            "skill": skill,
            "importance": "high" if i < 3 else "medium",
            "suggestion": f"Add '{skill}' to your Skills section or demonstrate it in work experience bullet points.",
        }
        for i, skill in enumerate(missing[:5])
    ]

    ats_tips = [
        "Use standard section headers: 'Experience', 'Education', 'Skills'",
        "Mirror keywords from the job description verbatim",
        "Avoid tables, columns, headers/footers — they confuse ATS parsers",
        "Use both acronyms and full forms (e.g., 'Machine Learning (ML)')",
        "Quantify achievements with numbers, percentages, or metrics",
    ]

    priority_actions = []
    if ats_score < 60:
        priority_actions.append(
            {"action": "Add missing skills to your Skills section", "impact": "high", "effort": "low"}
        )
    if word_count < 300:
        priority_actions.append(
            {"action": "Expand resume content with more detail", "impact": "high", "effort": "medium"}
        )
    priority_actions.append(
        {"action": "Tailor resume keywords to match the JD exactly", "impact": "high", "effort": "medium"}
    )

    return {
        "overall_assessment": (
            f"Your resume achieved an ATS score of {ats_score}/100. "
            f"{'Great alignment with the job requirements!' if ats_score >= 70 else 'There is room for improvement — focus on adding missing skills and mirroring JD keywords.'}"
        ),
        "strengths": strengths,
        "missing_skills_analysis": missing_analysis,
        "bullet_point_improvements": [
            {
                "original": "Worked on a project",
                "improved": "Designed and implemented [feature], reducing processing time by 30% and improving user satisfaction scores by 15%",
            }
        ],
        "ats_optimization_tips": ats_tips,
        "keyword_suggestions": missing[:10],
        "priority_actions": priority_actions,
        "_source": "fallback",
        "_error": error,
    }


JOB_GENERATION_PROMPT_TEMPLATE = """
You are a senior technical career strategist and executive recruiter.

The candidate has specified their skills, tech stack, and key project highlights below:
---
{user_input}
---

Based on their skillset and project background, generate a comprehensive JSON report containing:
1. "recommended_roles": Top 3-4 specific job titles best suited for this candidate profile.
2. "target_companies": 4-6 real-world tech companies (e.g. Stripe, Datadog, Snowflake, OpenAI, Google, AWS, etc.) actively hiring for this stack, with the sector and why they are a strong fit.
3. "generated_job_description": A full, highly detailed, realistic Job Description text tailored specifically to their skills and projects (including Role Summary, Key Responsibilities, and Technical Requirements).
4. "career_insights": 2-3 strategic recommendations for maximizing their market value.

Return ONLY valid JSON matching this EXACT structure:
{{
  "recommended_roles": ["Role Title 1", "Role Title 2", "Role Title 3"],
  "target_companies": [
    {{
      "name": "Company Name",
      "sector": "Sector/Domain",
      "why_fit": "Why candidate's skills and projects match this company's technology needs"
    }}
  ],
  "generated_job_description": "Full realistic Job Description text formatted with clear sections...",
  "career_insights": ["Insight 1", "Insight 2"]
}}
""".strip()


def generate_job_and_career_recommendations(user_input: str) -> dict:
    """
    Generate tailored Job Description, recommended roles, and target companies based on candidate's skills and projects.
    """
    if not GROQ_API_KEY:
        return _fallback_career_recommendations(user_input)

    prompt = JOB_GENERATION_PROMPT_TEMPLATE.format(user_input=user_input[:3000])

    try:
        client = _get_groq_client()
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert tech recruiter. Respond with valid JSON only, no markdown code blocks.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
            max_tokens=2048,
        )

        content = response.choices[0].message.content.strip()
        content = re.sub(r"^```(?:json)?\s*", "", content)
        content = re.sub(r"\s*```$", "", content)

        data = json.loads(content)
        data["_source"] = "groq"
        return data

    except (json.JSONDecodeError, Exception) as e:
        return _fallback_career_recommendations(user_input, error=str(e))


def _fallback_career_recommendations(user_input: str, error: str = "") -> dict:
    """Fallback career recommendation data when Groq API is unavailable."""
    return {
        "recommended_roles": [
            "Senior Full Stack Software Engineer",
            "Cloud Infrastructure & DevOps Engineer",
            "AI Solutions & Backend Engineer",
        ],
        "target_companies": [
            {
                "name": "Datadog",
                "sector": "Cloud Observability & SaaS",
                "why_fit": "High demand for Python, microservices, and high-concurrency backend experience.",
            },
            {
                "name": "Snowflake",
                "sector": "Data Cloud & Analytics",
                "why_fit": "Ideal fit for engineers with distributed systems, SQL, and backend API design skills.",
            },
            {
                "name": "Stripe",
                "sector": "Fintech & API Infrastructure",
                "why_fit": "Strong match for scalable microservices, robust testing, and security-focused architecture.",
            },
            {
                "name": "OpenAI",
                "sector": "Artificial Intelligence & LLMs",
                "why_fit": "Great match for Python, PyTorch, model deployment, and cloud data infrastructure.",
            },
        ],
        "generated_job_description": (
            "Job Title: Senior Software & AI Systems Engineer\n\n"
            "Role Summary:\n"
            "We are seeking a Senior Engineer to build, scale, and optimize high-performance microservices and AI-driven workflows.\n\n"
            "Key Responsibilities:\n"
            "• Architect and deploy production-grade web applications and REST/GraphQL APIs.\n"
            "• Manage containerized infrastructure using Docker, Kubernetes, and AWS.\n"
            "• Integrate machine learning models into real-time data pipelines.\n"
            "• Collaborate in Agile sprints and mentor junior engineering team members.\n\n"
            "Requirements:\n"
            "• 4+ years of software development experience with Python, React, and SQL databases.\n"
            "• Demonstrated project work in microservices, cloud deployments, or AI pipelines.\n"
            "• Bachelor's degree in Computer Science or equivalent hands-on project experience."
        ),
        "career_insights": [
            "Highlight quantified metrics (e.g. throughput increase, latency reduction) in your project descriptions.",
            "Add cloud infrastructure certifications (AWS/Azure) to stand out for senior roles.",
        ],
        "_source": "fallback",
        "_error": error,
    }
