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

GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


def _get_api_key() -> str:
    """Retrieve Groq API key from environment or Streamlit secrets."""
    key = os.getenv("GROQ_API_KEY", "")
    if not key:
        try:
            import streamlit as st
            if "GROQ_API_KEY" in st.secrets:
                key = st.secrets["GROQ_API_KEY"]
        except Exception:
            pass
    return key


def _get_groq_client():
    """Initialize and return a Groq client."""
    key = _get_api_key()
    try:
        from groq import Groq
        if not key:
            raise ValueError("GROQ_API_KEY not set in environment or Streamlit secrets.")
        return Groq(api_key=key)
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
    api_key = _get_api_key()
    if not api_key:
        return _fallback_career_recommendations(user_input, error="GROQ_API_KEY missing in environment / Streamlit secrets")

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
            temperature=0.7,
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
    """Dynamic fallback career recommendation engine when Groq API is unavailable or rate-limited."""
    raw_text = user_input.strip()
    text_lower = raw_text.lower()
    
    # Extract candidate skills (spaCy DB + raw words from text)
    extracted_skills = []
    try:
        from core.skill_extractor import extract_skills_spacy
        extracted_skills = extract_skills_spacy(raw_text)
    except Exception:
        pass

    raw_words = re.findall(r"\b[A-Za-z0-9+#.-]{2,20}\b", raw_text)
    word_candidates = []
    stop_words = {"with", "from", "and", "the", "for", "using", "built", "project", "projects", "stack", "tech", "skills", "experience", "work", "engineered", "developed", "application", "system", "example", "like", "such", "have", "that", "this"}
    for w in raw_words:
        if w.lower() not in stop_words and len(w) > 2:
            if w not in word_candidates and w.lower() not in [s.lower() for s in word_candidates]:
                word_candidates.append(w)

    combined_skills = extracted_skills + [w for w in word_candidates if w.lower() not in [s.lower() for s in extracted_skills]]
    skills_str = ", ".join(combined_skills[:8]) if combined_skills else "Software Engineering & System Architecture"
    top_skill = combined_skills[0] if combined_skills else "Software Development"

    # Domain Detection
    is_mobile = any(k in text_lower for k in ["flutter", "react native", "android", "ios", "kotlin", "swift", "mobile"])
    is_ai_ml = any(k in text_lower for k in ["pytorch", "tensorflow", "scikit-learn", "deep learning", "machine learning", "computer vision", "nlp", "yolo", "opencv", "huggingface", "llm", "ai"])
    is_data = any(k in text_lower for k in ["spark", "kafka", "pandas", "hadoop", "snowflake", "bigquery", "etl", "data pipeline", "data engineer"])
    is_devops = any(k in text_lower for k in ["docker", "kubernetes", "k8s", "terraform", "ansible", "jenkins", "ci/cd", "aws", "gcp", "azure", "devops"])
    is_frontend = any(k in text_lower for k in ["react", "vue", "angular", "next.js", "tailwind", "typescript", "css", "html", "frontend", "ui/ux"])
    is_cyber = any(k in text_lower for k in ["cybersecurity", "penetration testing", "wireshark", "metasploit", "soc", "siem", "ethical hacking", "infosec"])
    
    if is_mobile:
        roles = [
            f"Senior Mobile Application Engineer ({top_skill})",
            "Cross-Platform iOS & Android Developer",
            "Mobile Solutions Architect",
        ]
        companies = [
            {"name": "Uber", "sector": "Rideshare & Logistics Tech", "why_fit": f"High demand for mobile engineers experienced in {skills_str}."},
            {"name": "Spotify", "sector": "Digital Streaming & Media", "why_fit": f"Ideal match for building fluid, high-performance mobile UI apps using {skills_str}."},
            {"name": "DoorDash", "sector": "On-Demand Delivery & Logistics", "why_fit": f"Looking for mobile specialists with proven project experience in {skills_str}."},
            {"name": "Duolingo", "sector": "EdTech & Consumer Apps", "why_fit": f"Great fit for cross-platform app design and responsive UI features."},
        ]
        job_title = f"Senior Mobile Systems Engineer ({top_skill})"
    elif is_ai_ml:
        roles = [
            f"AI & Machine Learning Engineer ({top_skill})",
            "Applied Deep Learning Specialist",
            "AI Solutions & Model Deployment Engineer",
        ]
        companies = [
            {"name": "OpenAI", "sector": "Artificial Intelligence & LLMs", "why_fit": f"Strong alignment for AI model training and evaluation using {skills_str}."},
            {"name": "NVIDIA", "sector": "AI Hardware & Deep Learning Platforms", "why_fit": f"Demands expertise in machine learning frameworks like {skills_str}."},
            {"name": "Scale AI", "sector": "Data Infrastructure for AI", "why_fit": f"High fit for engineers building automated ML pipelines and data tools."},
            {"name": "Hugging Face", "sector": "Open Source AI & NLP", "why_fit": f"Ideal match for hands-on model fine-tuning and API integration."},
        ]
        job_title = f"Senior AI & Machine Learning Engineer ({top_skill})"
    elif is_data:
        roles = [
            f"Senior Data Engineer ({top_skill})",
            "Big Data & Analytics Specialist",
            "Data Platform Architect",
        ]
        companies = [
            {"name": "Snowflake", "sector": "Data Cloud & Analytics", "why_fit": f"High demand for large-scale data modeling and processing using {skills_str}."},
            {"name": "Databricks", "sector": "Data Intelligence & Lakehouse", "why_fit": f"Ideal fit for distributed data pipelines and analytics systems."},
            {"name": "Palantir", "sector": "Enterprise Data Platforms", "why_fit": f"Great match for robust ETL workflows and complex data integration."},
            {"name": "Stripe", "sector": "Fintech & Financial Data", "why_fit": f"Strong alignment for real-time transaction processing and analytics."},
        ]
        job_title = f"Senior Data Platform Engineer ({top_skill})"
    elif is_devops:
        roles = [
            f"Cloud Infrastructure & DevOps Engineer ({top_skill})",
            "Site Reliability Engineer (SRE)",
            "Cloud Platform Architect",
        ]
        companies = [
            {"name": "Datadog", "sector": "Cloud Observability & SaaS", "why_fit": f"High demand for infrastructure automation and container orchestration using {skills_str}."},
            {"name": "HashiCorp", "sector": "Cloud Infrastructure Automation", "why_fit": f"Ideal fit for Infrastructure-as-Code and multi-cloud management."},
            {"name": "AWS (Amazon)", "sector": "Cloud Infrastructure & Services", "why_fit": f"Seeking engineers proficient in containerization, scaling, and CI/CD."},
            {"name": "Cloudflare", "sector": "Edge Computing & Security", "why_fit": f"Great match for high-availability networking and zero-trust systems."},
        ]
        job_title = f"Senior Cloud Infrastructure Engineer ({top_skill})"
    elif is_frontend:
        roles = [
            f"Senior Frontend & Web Engineer ({top_skill})",
            "Full Stack UI Specialist",
            "Frontend Systems Architect",
        ]
        companies = [
            {"name": "Vercel", "sector": "Frontend Platform & Edge Systems", "why_fit": f"High demand for modern web application performance using {skills_str}."},
            {"name": "Figma", "sector": "Collaborative Design Software", "why_fit": f"Ideal fit for building complex, interactive user interfaces and component libraries."},
            {"name": "Canva", "sector": "Visual Communication & SaaS", "why_fit": f"Seeking UI engineers skilled in responsive design and state management."},
            {"name": "Airbnb", "sector": "Consumer Web & Marketplace", "why_fit": f"Great match for component-driven architecture and web optimization."},
        ]
        job_title = f"Senior Frontend & UI Engineer ({top_skill})"
    elif is_cyber:
        roles = [
            f"Cybersecurity & Penetration Testing Engineer ({top_skill})",
            "Information Security Specialist",
            "SOC & Security Automation Engineer",
        ]
        companies = [
            {"name": "CrowdStrike", "sector": "Endpoint Security & Threat Intelligence", "why_fit": f"High demand for threat analysis and security automation using {skills_str}."},
            {"name": "Palo Alto Networks", "sector": "Enterprise Network Security", "why_fit": f"Ideal match for vulnerability assessment and security policy enforcement."},
            {"name": "Cloudflare", "sector": "Web Application Firewall & Security", "why_fit": f"Seeking security professionals skilled in packet analysis and network defense."},
            {"name": "Mandiant", "sector": "Incident Response & Cybersecurity", "why_fit": f"Great fit for hands-on penetration testing and forensics."},
        ]
        job_title = f"Senior Security & Systems Engineer ({top_skill})"
    else:
        roles = [
            f"Senior Software Engineer ({top_skill})",
            "Full Stack Systems Developer",
            "Backend & API Engineer",
        ]
        companies = [
            {"name": "Stripe", "sector": "Fintech & API Infrastructure", "why_fit": f"High demand for scalable microservices and clean code architecture using {skills_str}."},
            {"name": "Datadog", "sector": "Cloud Observability & SaaS", "why_fit": f"Ideal fit for software engineers with hands-on experience in {skills_str}."},
            {"name": "Snowflake", "sector": "Data Cloud & Enterprise Software", "why_fit": f"Strong alignment for scalable backend systems and database engineering."},
            {"name": "Atlassian", "sector": "Developer Tools & Enterprise SaaS", "why_fit": f"Great match for building resilient API services and collaborative tools."},
        ]
        job_title = f"Senior Software Engineer ({top_skill})"

    snippet = user_input.strip()[:250].replace('\n', ' ')
    generated_jd = (
        f"Job Title: {job_title}\n\n"
        f"Role Summary:\n"
        f"We are looking for a skilled professional with expertise in {skills_str} to lead key development initiatives. "
        f"Based on your profile highlights (\"{snippet}...\"), this role focuses on building production-grade solutions, "
        f"optimizing application performance, and maintaining modern engineering standards.\n\n"
        f"Key Responsibilities:\n"
        f"• Design, build, and maintain scalable applications and services utilizing {top_skill}.\n"
        f"• Implement best practices for code quality, testing, and continuous integration.\n"
        f"• Collaborate closely with cross-functional product and engineering teams.\n"
        f"• Deliver robust technical solutions aligned with candidate background: {skills_str}.\n\n"
        f"Requirements:\n"
        f"• 3+ years of professional development experience in {skills_str}.\n"
        f"• Demonstrated track record in software design, API integration, or system architecture.\n"
        f"• Strong analytical skills and familiarity with modern development tools."
    )

    career_insights = [
        f"Emphasize your hands-on experience with {skills_str} at the top of your resume summary.",
        "Quantify project outcomes with numbers (e.g., 'reduced latency by 25%', 'served 10k users') to increase ATS ranking.",
        f"Target roles specializing in {top_skill} to maximize your salary negotiation leverage.",
    ]

    return {
        "recommended_roles": roles,
        "target_companies": companies,
        "generated_job_description": generated_jd,
        "career_insights": career_insights,
        "_source": "dynamic_fallback",
        "_error": error,
    }
