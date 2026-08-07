# ⚡ JobFit ATS AI — Next-Gen AI Resume Intelligence & ATS Command Center
App URL - https://jobfit-ats-ai-2ypevkvbjjz2l6wj4pfruh.streamlit.app

**JobFit ATS AI** is an end-to-end, AI-powered Applicant Tracking System (ATS) resume optimization platform. It parses candidate resumes (PDF/DOCX), evaluates them against target Job Descriptions using hybrid semantic vector search and NLP phrase matching, provides actionable AI career feedback, rewrites resumes to cover skill gaps, and exports 100% ATS-compliant PDF and DOCX files.

---

## ✨ Key Features

- 📄 **Multi-Format Document Parser**: Extracts text and auto-segments sections (`Summary`, `Experience`, `Education`, `Skills`, `Projects`) from PDF (PyMuPDF) and DOCX files.
- 🎯 **Hybrid ATS Scoring Engine**: Computes a weighted 0–100 match score across 6 key dimensions:
  - **40%** Semantic Vector Similarity (`sentence-transformers/all-mpnet-base-v2`)
  - **25%** Skill Match & Gap Analysis (`spaCy PhraseMatcher` + 1000+ Skill DB)
  - **15%** Work Experience & Seniority Level Alignment
  - **10%** Education Degree Match
  - **5%** Keyword Density
  - **5%** ATS Readability & Formatting Compliance
- 💡 **AI Career Coach**: Powered by **Groq API** (`llama-3.3-70b-versatile`) to deliver structured strengths, priority action steps, and quantified bullet point rewrites.
- ✍️ **1-Click AI Resume Rewriter**: Dynamically transforms unstructured resume text into a high-impact, ATS-optimized JSON resume structure seamlessly incorporating missing skills.
- 📥 **ATS-Compliant Document Exporter**: Generates 100% ATS-readable **PDF** (via ReportLab flowables) and **DOCX** (via `python-docx`).
- 📊 **Interactive Analytics**: Features dynamic Plotly gauge charts, radar charts, and score breakdown cards.

