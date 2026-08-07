# ⚡ JobFit ATS AI — Next-Gen AI Resume Intelligence & ATS Command Center

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

---

## 🛠️ Tech Stack

- **Frontend / UI**: Streamlit, Custom Neo-Glassmorphic CSS, Plotly
- **NLP & Extraction**: spaCy (`en_core_web_sm`), SkillNer, PyMuPDF, python-docx
- **Vector Embeddings**: Sentence Transformers (`all-mpnet-base-v2`), NumPy, Scikit-learn
- **AI / LLM Engine**: Groq Cloud API (`llama-3.3-70b-versatile`)
- **Document Export**: ReportLab, python-docx
- **Deployment**: Render Blueprint (`render.yaml`)

---

## 🚀 Quick Start (Local Setup)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/surya-X-13/JobFit-ATS-AI.git
   cd JobFit-ATS-AI
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies & download spaCy model**:
   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

4. **Configure environment variables**:
   Create a `.env` file in the root directory:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   GROQ_MODEL=llama-3.3-70b-versatile
   ```

5. **Run the app**:
   ```bash
   streamlit run app.py
   ```

---

## 🌐 Deploy to Render

This project is pre-configured with `render.yaml` and `build.sh` for easy deployment on Render:

1. Push this repository to GitHub.
2. Go to [Render Dashboard](https://dashboard.render.com/) → **New +** → **Blueprint**.
3. Connect `surya-X-13/JobFit-ATS-AI`.
4. Add your `GROQ_API_KEY` environment variable when prompted and deploy!
