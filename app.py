"""
app.py — ATS Resume Scorer Pro
Next-Gen Command Center Layout with AI Career Generator & 1-Click ATS Resume Rewriter Exporter
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import time
import io
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

# ─────────────────────────────────────────────────────────
# Page Configuration
# ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ATS Command Center | AI Resume Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────
# Session State Initialization
# ─────────────────────────────────────────────────────────
if "results" not in st.session_state:
    st.session_state.results = None
if "feedback" not in st.session_state:
    st.session_state.feedback = None
if "career_recommendations" not in st.session_state:
    st.session_state.career_recommendations = None
if "transferred_jd" not in st.session_state:
    st.session_state.transferred_jd = ""
if "rewritten_resume" not in st.session_state:
    st.session_state.rewritten_resume = None

# ─────────────────────────────────────────────────────────
# Neo-Glassmorphic Design Tokens & CSS
# ─────────────────────────────────────────────────────────
T = {
    "bg_main": "#050512",
    "bg_card": "rgba(14, 14, 36, 0.75)",
    "bg_card_alt": "rgba(20, 20, 52, 0.85)",
    "text_main": "#f5f5ff",
    "text_muted": "#8c8cb8",
    "accent_purple": "#8a7cf8",
    "accent_pink": "#ff5c93",
    "accent_cyan": "#00e5ff",
    "accent_emerald": "#00e676",
    "accent_amber": "#ffb300",
    "border_glow": "rgba(138, 124, 248, 0.28)",
    "border_hover": "rgba(138, 124, 248, 0.65)",
    "shadow_glow": "rgba(138, 124, 248, 0.25)",
}


def inject_custom_styles():
    st.markdown(
        f"""
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@500;600;700;800&display=swap');

/* ── Global Reset & Ambient Mesh ── */
*, *::before, *::after {{ box-sizing: border-box; }}

.stApp {{
    background: 
        radial-gradient(ellipse at 15% 15%, rgba(138, 124, 248, 0.16) 0%, transparent 42%),
        radial-gradient(ellipse at 85% 85%, rgba(255, 92, 147, 0.14) 0%, transparent 42%),
        radial-gradient(ellipse at 50% 30%, rgba(0, 229, 255, 0.06) 0%, transparent 55%),
        {T['bg_main']} !important;
    font-family: 'Plus Jakarta Sans', sans-serif;
    color: {T['text_main']};
}}

.block-container {{
    padding-top: 1rem !important;
    padding-bottom: 3.5rem !important;
    max-width: 1380px !important;
}}

/* Hide Streamlit Chrome */
[data-testid="stSidebar"] {{ display: none !important; }}
[data-testid="collapsedControl"] {{ display: none !important; }}
#MainMenu, footer, header, .stDeployButton {{ display: none !important; }}

/* ── Command Header Bar ── */
.command-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 28px;
    background: rgba(14, 14, 34, 0.75);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid {T['border_glow']};
    border-radius: 22px;
    margin-bottom: 24px;
    box-shadow: 0 12px 40px rgba(0,0,0,0.5);
}}
.header-brand {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 24px;
    font-weight: 800;
    margin: 0;
    background: linear-gradient(135deg, #8a7cf8 0%, #ff5c93 50%, #00e5ff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.5px;
}}
.header-tagline {{
    font-size: 12px;
    color: {T['text_muted']};
    margin: 2px 0 0;
    font-weight: 500;
}}
.status-pill {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(0, 230, 118, 0.1);
    color: {T['accent_emerald']};
    border: 1px solid rgba(0, 230, 118, 0.35);
    padding: 6px 16px;
    border-radius: 30px;
    font-size: 12px;
    font-weight: 600;
}}
.status-dot {{
    width: 8px;
    height: 8px;
    background-color: {T['accent_emerald']};
    border-radius: 50%;
    box-shadow: 0 0 10px {T['accent_emerald']};
    animation: pulseDot 2s infinite;
}}
@keyframes pulseDot {{
    0%, 100% {{ opacity: 1; transform: scale(1); }}
    50% {{ opacity: 0.4; transform: scale(1.3); }}
}}

/* ── Custom Tabs ── */
.stTabs [data-baseweb="tab-list"] {{
    gap: 12px;
    background: rgba(14, 14, 34, 0.65);
    padding: 8px;
    border-radius: 20px;
    border: 1px solid {T['border_glow']};
    margin-bottom: 24px;
}}
.stTabs [data-baseweb="tab"] {{
    height: 48px;
    border-radius: 14px;
    color: {T['text_muted']};
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
    font-size: 14px;
    border: none !important;
    padding: 0 20px;
    transition: all 0.3s ease;
}}
.stTabs [aria-selected="true"] {{
    background: linear-gradient(135deg, rgba(138, 124, 248, 0.3), rgba(255, 92, 147, 0.3)) !important;
    color: #ffffff !important;
    border: 1px solid {T['border_hover']} !important;
    box-shadow: 0 6px 20px {T['shadow_glow']};
}}

/* ── Hero Workbench ── */
.workbench-hero {{
    text-align: center !important;
    margin-bottom: 28px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}}
.hero-title {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 38px;
    font-weight: 800;
    margin-bottom: 8px;
    background: linear-gradient(135deg, #ffffff 0%, #a0a0d0 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -1px;
    text-align: center !important;
}}
.hero-subtitle {{
    font-size: 15px;
    color: {T['text_muted']};
    max-width: 640px;
    margin: 0 auto;
    line-height: 1.6;
    text-align: center !important;
}}

/* ── Neo Glass Cards ── */
.neo-card {{
    background: {T['bg_card']};
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid {T['border_glow']};
    border-radius: 24px;
    padding: 26px;
    margin-bottom: 22px;
    transition: all 0.35s ease;
    box-shadow: 0 12px 35px rgba(0, 0, 0, 0.4);
}}
.neo-card:hover {{
    border-color: {T['border_hover']};
    box-shadow: 0 18px 45px {T['shadow_glow']};
}}

/* ── Step Card Header ── */
.step-header {{
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    margin-bottom: 18px;
    text-align: center;
}}
.step-badge {{
    width: 34px;
    height: 34px;
    border-radius: 12px;
    background: linear-gradient(135deg, {T['accent_purple']}, {T['accent_pink']});
    color: #ffffff;
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 800;
    font-size: 15px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 15px {T['shadow_glow']};
}}
.step-title {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 18px;
    font-weight: 700;
    color: {T['text_main']};
    margin: 0;
    text-align: center;
}}

/* ── Form Styling ── */
[data-testid="stFileUploader"] {{
    background: rgba(10, 10, 26, 0.6) !important;
    border: 2px dashed rgba(138, 124, 248, 0.3) !important;
    border-radius: 18px !important;
    padding: 16px !important;
    transition: all 0.3s ease !important;
}}
[data-testid="stFileUploader"]:hover {{
    border-color: {T['accent_purple']} !important;
    background: rgba(16, 16, 40, 0.8) !important;
}}

.stTextArea textarea {{
    background: rgba(10, 10, 26, 0.75) !important;
    color: {T['text_main']} !important;
    border: 1px solid {T['border_glow']} !important;
    border-radius: 16px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 13.5px !important;
    padding: 16px !important;
    transition: all 0.3s;
}}
.stTextArea textarea:focus {{
    border-color: {T['accent_purple']} !important;
    box-shadow: 0 0 0 3px rgba(138, 124, 248, 0.25) !important;
}}

/* ── Action Buttons ── */
.stButton > button {{
    background: linear-gradient(135deg, #8a7cf8 0%, #ff5c93 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 16px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 800 !important;
    font-size: 15px !important;
    padding: 16px 32px !important;
    width: 100% !important;
    cursor: pointer !important;
    transition: all 0.35s ease !important;
    box-shadow: 0 8px 30px rgba(138, 124, 248, 0.45) !important;
    letter-spacing: 0.6px;
}}
.stButton > button:hover {{
    transform: translateY(-3px) scale(1.01) !important;
    box-shadow: 0 14px 40px rgba(138, 124, 248, 0.65) !important;
}}

/* ── KPI Cards ── */
.kpi-card {{
    background: rgba(18, 18, 48, 0.8);
    backdrop-filter: blur(14px);
    border: 1px solid {T['border_glow']};
    border-radius: 20px;
    padding: 22px;
    text-align: center;
    transition: all 0.3s ease;
}}
.kpi-card:hover {{
    border-color: {T['border_hover']};
    transform: translateY(-3px);
}}
.kpi-title {{
    font-size: 12px;
    font-weight: 700;
    color: {T['text_muted']};
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 6px;
}}
.kpi-value {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 36px;
    font-weight: 800;
    color: {T['text_main']};
    line-height: 1.1;
}}
.kpi-sub {{
    font-size: 12px;
    font-weight: 600;
    margin-top: 6px;
}}

/* ── Company Fit Card ── */
.company-card {{
    background: rgba(22, 22, 54, 0.8);
    border: 1px solid {T['border_glow']};
    border-radius: 18px;
    padding: 18px 22px;
    margin-bottom: 14px;
    transition: all 0.3s ease;
}}
.company-card:hover {{
    border-color: {T['border_hover']};
    transform: translateY(-2px);
    box-shadow: 0 8px 25px {T['shadow_glow']};
}}

/* ── Pill Tags ── */
.tag-pill {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    border-radius: 24px;
    padding: 6px 14px;
    font-size: 12.5px;
    font-weight: 600;
    margin: 4px;
    transition: all 0.25s ease;
}}
.tag-matched {{
    background: rgba(0, 230, 118, 0.12);
    color: {T['accent_emerald']};
    border: 1px solid rgba(0, 230, 118, 0.35);
}}
.tag-missing {{
    background: rgba(255, 92, 147, 0.12);
    color: {T['accent_pink']};
    border: 1px solid rgba(255, 92, 147, 0.35);
}}
.tag-extra {{
    background: rgba(0, 229, 255, 0.12);
    color: {T['accent_cyan']};
    border: 1px solid rgba(0, 229, 255, 0.35);
}}

/* Responsive */
@media (max-width: 768px) {{
    .hero-title {{ font-size: 28px !important; }}
    .hero-subtitle {{ font-size: 13px !important; }}
    .kpi-value {{ font-size: 26px !important; }}
}}
</style>
""",
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────
# Plotly Chart Builders
# ─────────────────────────────────────────────────────────
def build_radar_chart(components: dict) -> go.Figure:
    labels = {
        "semantic_similarity": "Semantic",
        "skill_match": "Skill Match",
        "experience_match": "Experience",
        "education_match": "Education",
        "formatting_score": "Formatting",
        "keyword_density": "Keywords",
    }
    cats = [labels.get(k, k) for k in components]
    vals = [round(v, 1) for v in components.values()]
    cats_closed = cats + [cats[0]]
    vals_closed = vals + [vals[0]]

    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=vals_closed,
            theta=cats_closed,
            fill="toself",
            fillcolor="rgba(138, 124, 248, 0.22)",
            line={"color": T["accent_purple"], "width": 2.5},
            name="Candidate",
            hovertemplate="%{theta}: %{r:.1f}%<extra></extra>",
        )
    )
    target = [75] * len(cats)
    fig.add_trace(
        go.Scatterpolar(
            r=target + [target[0]],
            theta=cats_closed,
            line={"color": T["accent_emerald"], "width": 1.5, "dash": "dot"},
            fill="toself",
            fillcolor="rgba(0, 230, 118, 0.05)",
            name="Target (75%)",
            hoverinfo="skip",
        )
    )
    fig.update_layout(
        polar={
            "radialaxis": {
                "visible": True,
                "range": [0, 100],
                "tickfont": {"size": 9, "color": T["text_muted"]},
                "gridcolor": "rgba(138, 124, 248, 0.15)",
            },
            "angularaxis": {
                "tickfont": {"size": 11, "color": T["text_main"], "family": "Space Grotesk"},
                "gridcolor": "rgba(138, 124, 248, 0.15)",
            },
            "bgcolor": "rgba(0,0,0,0)",
        },
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=True,
        legend={"font": {"size": 11, "color": T["text_muted"]}, "bgcolor": "rgba(0,0,0,0)"},
        height=290,
        margin={"t": 20, "b": 20, "l": 30, "r": 30},
    )
    return fig


def build_horizontal_bars(components: dict, weights: dict) -> go.Figure:
    labels = {
        "semantic_similarity": "Semantic Relevance",
        "skill_match": "Skill Alignment",
        "experience_match": "Experience Match",
        "education_match": "Education Requirement",
        "formatting_score": "ATS Formatting",
        "keyword_density": "Keyword Frequency",
    }
    comp_labels = [labels.get(k, k) for k in components]
    comp_values = list(components.values())
    comp_weights = [f"{int(weights[k]*100)}% Weight" for k in components]

    colors = [
        T["accent_emerald"] if v >= 75 else T["accent_cyan"] if v >= 60 else T["accent_amber"] if v >= 45 else T["accent_pink"]
        for v in comp_values
    ]

    fig = go.Figure(
        go.Bar(
            x=comp_values,
            y=comp_labels,
            orientation="h",
            marker={"color": colors, "line": {"width": 0}},
            text=[f"{v:.1f}%" for v in comp_values],
            textposition="inside",
            textfont={"color": "#ffffff", "size": 12, "family": "Space Grotesk"},
            customdata=comp_weights,
            hovertemplate="%{y}: %{x:.1f}% (%{customdata})<extra></extra>",
        )
    )
    fig.update_layout(
        xaxis={"range": [0, 100], "gridcolor": "rgba(138, 124, 248, 0.12)", "tickfont": {"color": T["text_muted"], "size": 10}},
        yaxis={"tickfont": {"color": T["text_main"], "size": 12, "family": "Space Grotesk"}},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=290,
        margin={"t": 10, "b": 20, "l": 10, "r": 20},
        bargap=0.35,
    )
    return fig


# ─────────────────────────────────────────────────────────
# Main Layout Renderers
# ─────────────────────────────────────────────────────────
def render_header():
    st.markdown(
        """
        <div class="command-header">
            <div>
                <p class="header-brand">⚡ ATS COMMAND CENTER</p>
                <p class="header-tagline">AI Resume Diagnostics &nbsp;•&nbsp; Hybrid Scoring 2.0 &nbsp;•&nbsp; Job & Role Generator</p>
            </div>
            <div class="status-pill">
                <span class="status-dot"></span>
                AI Intelligence Active
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_ats_scanner_tab():
    st.markdown(
        """
        <div class="workbench-hero">
            <h1 class="hero-title">Scan & Optimize Your Resume for ATS</h1>
            <p class="hero-subtitle">
                Upload your resume alongside any target job description to run deep semantic analysis,
                skill gap detection, and instant AI coaching recommendations.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([1, 1], gap="medium")

    with col1:
        st.markdown(
            """
            <div class="neo-card">
                <div class="step-header">
                    <div class="step-badge">1</div>
                    <p class="step-title">Upload Candidate Resume</p>
                </div>
            """,
            unsafe_allow_html=True,
        )
        uploaded_file = st.file_uploader(
            label="Resume (PDF or DOCX)",
            type=["pdf", "docx"],
            label_visibility="collapsed",
            key="resume_file",
        )
        if uploaded_file:
            st.markdown(
                f'<div style="font-size:12px;color:{T["accent_emerald"]};font-weight:600;margin-top:8px;">'
                f'✅ File Attached: {uploaded_file.name} ({uploaded_file.size/1024:.1f} KB)</div>',
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown(
            """
            <div class="neo-card">
                <div class="step-header">
                    <div class="step-badge">2</div>
                    <p class="step-title">Target Job Description</p>
                </div>
            """,
            unsafe_allow_html=True,
        )

        if "jd_input" not in st.session_state and st.session_state.transferred_jd:
            st.session_state.jd_input = st.session_state.transferred_jd

        jd_text = st.text_area(
            label="Job Description",
            height=200,
            placeholder="Paste complete job description text here...\n\n(Tip: Or generate one using the 'AI Job & Target Company Generator' tab above!)",
            label_visibility="collapsed",
            key="jd_input",
        )
        if jd_text:
            wc = len(jd_text.split())
            st.markdown(
                f'<div style="font-size:11px;color:{T["text_muted"]};margin-top:4px;">{wc} words detected</div>',
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    # Action Row with Primary Scan button
    b_col1, b_col2, b_col3 = st.columns([1, 2, 1])

    with b_col2:
        analyze_btn = st.button(
            "⚡ RUN ATS DIAGNOSTIC SCAN",
            key="analyze_btn",
            disabled=(uploaded_file is None or not (jd_text or "").strip()),
            use_container_width=True,
        )

    return uploaded_file, jd_text, analyze_btn


def render_dashboard(results: dict, feedback: dict):
    score = results["ats_score"]
    score_color = results["score_color"]
    score_label = results["score_label"]
    components = results["components"]
    weights = results["weights"]
    metrics = results["metrics"]
    matched = results["matched_skills"]
    missing = results["missing_skills"]
    extra = results["extra_skills"]

    # ── Section 1: KPI Hero Banner ──
    k1, k2, k3, k4 = st.columns(4, gap="medium")
    with k1:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-title">Overall ATS Match</div>
                <div class="kpi-value" style="color:{score_color};">{score:.1f}</div>
                <div class="kpi-sub" style="color:{score_color};">{score_label.upper()}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with k2:
        sem = components.get("semantic_similarity", 0)
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-title">Semantic Match</div>
                <div class="kpi-value" style="color:{T['accent_purple']};">{sem:.1f}%</div>
                <div class="kpi-sub" style="color:{T['text_muted']};">Vector Similarity</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with k3:
        sk_ratio = f"{len(matched)} / {len(matched)+len(missing)}" if (matched or missing) else "N/A"
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-title">Skill Match Ratio</div>
                <div class="kpi-value" style="color:{T['accent_cyan']};">{sk_ratio}</div>
                <div class="kpi-sub" style="color:{T['text_muted']};">{len(matched)} Matched</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with k4:
        fmt = metrics.get("formatting_score", 0)
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-title">Format Score</div>
                <div class="kpi-value" style="color:{T['accent_emerald']};">{fmt:.0f}/100</div>
                <div class="kpi-sub" style="color:{T['text_muted']};">ATS Readiness</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Section 2: 2x2 Command Grid View ──
    g_col1, g_col2 = st.columns([1, 1], gap="medium")

    with g_col1:
        st.markdown('<div class="neo-card">', unsafe_allow_html=True)
        st.markdown(
            '<p style="font-family:\'Space Grotesk\';font-size:17px;font-weight:700;margin:0 0 12px;text-align:center;">'
            '🕸️ Multi-Vector Benchmark Radar</p>',
            unsafe_allow_html=True,
        )
        radar = build_radar_chart(components)
        st.plotly_chart(radar, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with g_col2:
        st.markdown('<div class="neo-card">', unsafe_allow_html=True)
        st.markdown(
            '<p style="font-family:\'Space Grotesk\';font-size:17px;font-weight:700;margin:0 0 12px;text-align:center;">'
            '📈 Component Weight Analysis</p>',
            unsafe_allow_html=True,
        )
        bars = build_horizontal_bars(components, weights)
        st.plotly_chart(bars, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Section 3: Skill Gap Matrix & Groq AI Coach ──
    s_col1, s_col2 = st.columns([1, 1], gap="medium")

    with s_col1:
        st.markdown('<div class="neo-card">', unsafe_allow_html=True)
        st.markdown(
            '<p style="font-family:\'Space Grotesk\';font-size:18px;font-weight:700;margin:0 0 14px;text-align:center;">'
            '🛠️ Skill Alignment Matrix</p>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<p style="font-size:13px;font-weight:700;color:{T["accent_emerald"]};margin-bottom:6px;text-align:center;">'
            f'✅ Matched Skills ({len(matched)})</p>',
            unsafe_allow_html=True,
        )
        if matched:
            m_tags = '<div style="text-align:center;">' + " ".join(f'<span class="tag-pill tag-matched">✓ {s}</span>' for s in matched) + '</div>'
            st.markdown(m_tags, unsafe_allow_html=True)
        else:
            st.markdown(f'<p style="color:{T["text_muted"]};font-size:12px;text-align:center;">No skills matched</p>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(
            f'<p style="font-size:13px;font-weight:700;color:{T["accent_pink"]};margin-bottom:6px;text-align:center;">'
            f'❌ Missing Skills ({len(missing)})</p>',
            unsafe_allow_html=True,
        )
        if missing:
            mis_tags = '<div style="text-align:center;">' + " ".join(f'<span class="tag-pill tag-missing">✗ {s}</span>' for s in missing) + '</div>'
            st.markdown(mis_tags, unsafe_allow_html=True)
        else:
            st.markdown(f'<p style="color:{T["accent_emerald"]};font-size:12px;text-align:center;">🎉 All required skills matched!</p>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(
            f'<p style="font-size:13px;font-weight:700;color:{T["accent_cyan"]};margin-bottom:6px;text-align:center;">'
            f'💡 Extra Resume Skills ({len(extra)})</p>',
            unsafe_allow_html=True,
        )
        if extra:
            ex_tags = '<div style="text-align:center;">' + " ".join(f'<span class="tag-pill tag-extra">+ {s}</span>' for s in list(extra)[:15]) + '</div>'
            st.markdown(ex_tags, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    with s_col2:
        st.markdown('<div class="neo-card">', unsafe_allow_html=True)
        st.markdown(
            '<p style="font-family:\'Space Grotesk\';font-size:18px;font-weight:700;margin:0 0 14px;text-align:center;">'
            '🤖 AI Executive Feedback</p>',
            unsafe_allow_html=True,
        )

        if feedback:
            if assessment := feedback.get("overall_assessment"):
                st.markdown(
                    f"""<div class="ai-box">
                    💬 <b>Assessment Summary:</b><br><br>{assessment}
                    </div>""",
                    unsafe_allow_html=True,
                )

            with st.expander("💪 Highlighted Strengths", expanded=True):
                for st_item in feedback.get("strengths", []):
                    st.markdown(f'<div style="font-size:13px;padding:4px 0;">✅ {st_item}</div>', unsafe_allow_html=True)

            with st.expander("✏️ Bullet Point Before & After"):
                for item in feedback.get("bullet_point_improvements", []):
                    st.markdown(
                        f"""<div class="ai-bullet">
                        <div style="color:{T['accent_pink']};font-size:12.5px;margin-bottom:6px;">❌ Before: {item.get('original','')}</div>
                        <div style="color:{T['accent_emerald']};font-size:12.5px;">✅ Improved: {item.get('improved','')}</div>
                        </div>""",
                        unsafe_allow_html=True,
                    )

            with st.expander("📌 Priority Action Roadmap"):
                for act in feedback.get("priority_actions", []):
                    st.markdown(
                        f"""<div style="padding:8px 0;border-bottom:1px solid {T['border_glow']};font-size:13px;">
                        🎯 <b>{act.get('action','')}</b> &nbsp;•&nbsp; 
                        <span style="color:{T['accent_cyan']};">Impact: {act.get('impact','').upper()}</span>
                        </div>""",
                        unsafe_allow_html=True,
                    )

        st.markdown('</div>', unsafe_allow_html=True)

    # ── Section 4: 1-Click AI Resume Rewriter & ATS Exporter ──
    st.markdown("<hr style='border-color:rgba(138,124,248,0.25);margin:28px 0;'>", unsafe_allow_html=True)
    st.markdown('<div class="neo-card">', unsafe_allow_html=True)
    st.markdown(
        '<p style="font-family:\'Space Grotesk\';font-size:20px;font-weight:700;margin:0 0 8px;text-align:center;">'
        '✨ 1-Click AI Resume Rewriter & ATS Exporter</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<p style="font-size:13.5px;color:{T["text_muted"]};margin-bottom:20px;text-align:center;">'
        'Automatically incorporate missing target skills, optimize experience bullet points with quantified metrics, '
        'and download an ATS-compliant PDF or editable Word document.</p>',
        unsafe_allow_html=True,
    )

    r_col1, r_col2, r_col3 = st.columns([1, 2, 1])
    with r_col2:
        rewrite_btn = st.button(
            "⚡ REWRITE & OPTIMIZE RESUME WITH AI",
            key="rewrite_resume_btn",
            use_container_width=True,
        )

    if rewrite_btn:
        with st.spinner("🤖 AI is restructuring your resume and incorporating missing target skills..."):
            try:
                from core.rewriter import rewrite_resume_with_ai
                rewritten_data = rewrite_resume_with_ai(
                    results.get("resume_full_text", ""),
                    results.get("target_jd", ""),
                    results
                )
                st.session_state.rewritten_resume = rewritten_data
                st.toast("✅ Resume Successfully Rewritten & Optimized!", icon="🎉")
            except Exception as e:
                st.error(f"Rewriting failed: {str(e)}")

    if st.session_state.rewritten_resume:
        rew = st.session_state.rewritten_resume

        # Download Buttons Row
        try:
            from core.exporter import export_to_pdf, export_to_docx
            pdf_bytes = export_to_pdf(rew)
            docx_bytes = export_to_docx(rew)

            d_col1, d_col2 = st.columns(2, gap="medium")
            with d_col1:
                st.download_button(
                    label="📥 Download ATS PDF Resume (.pdf)",
                    data=pdf_bytes,
                    file_name="ATS_Optimized_Resume.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    key="dl_pdf_btn",
                )
            with d_col2:
                st.download_button(
                    label="📥 Download Editable Resume (.docx)",
                    data=docx_bytes,
                    file_name="ATS_Optimized_Resume.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                    key="dl_docx_btn",
                )
        except Exception as exp_err:
            st.error(f"Failed to generate download files: {str(exp_err)}")

        st.markdown("<br>", unsafe_allow_html=True)

        # Preview of Rewritten Content
        with st.expander("📄 View Rewritten Resume Content Preview", expanded=True):
            st.markdown(f"### {rew.get('full_name', 'CANDIDATE NAME')}")
            st.markdown(f"*{rew.get('contact_info', '')}*")
            st.markdown("---")
            st.markdown(f"**Professional Summary:**\n{rew.get('professional_summary', '')}")
            st.markdown("---")
            st.markdown("**Technical Skills Matrix:**")
            for cat, sk_l in rew.get("technical_skills", {}).items():
                sk_str = ", ".join(sk_l) if isinstance(sk_l, list) else str(sk_l)
                st.markdown(f"- **{cat}:** {sk_str}")
            st.markdown("---")
            st.markdown("**Optimized Experience Bullets:**")
            for exp in rew.get("work_experience", []):
                st.markdown(f"**{exp.get('title','')} | {exp.get('company','')}** *({exp.get('location_dates','')})*")
                for b in exp.get("bullet_points", []):
                    st.markdown(f"• {b}")

    st.markdown('</div>', unsafe_allow_html=True)


def render_career_generator_tab():
    st.markdown(
        """
        <div class="workbench-hero" style="text-align: center;">
            <h1 class="hero-title" style="text-align: center;">AI Job & Company Match Generator</h1>
            <p class="hero-subtitle" style="text-align: center; margin: 0 auto;">
                Enter your technical skills, technologies, and key project highlights.
                Advanced AI will generate tailored Job Descriptions, target company roles, and high-match companies hiring for your stack.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="neo-card">', unsafe_allow_html=True)
    st.markdown(
        '<p style="font-family:\'Space Grotesk\';font-size:18px;font-weight:700;margin:0 0 10px;text-align:center;">'
        '💼 Enter Your Skills & Project Highlights</p>',
        unsafe_allow_html=True,
    )

    user_skills_input = st.text_area(
        label="Skills & Projects Text Input",
        height=180,
        placeholder="Example:\n- Tech Stack: Python, FastAPI, React, PostgreSQL, Docker, AWS (EC2, EKS), PyTorch\n- Projects: Built a real-time data streaming pipeline with Apache Kafka. Engineered an AI search engine using sentence-transformers and FastAPI.",
        label_visibility="collapsed",
        key="career_skills_input",
    )

    gen_col1, gen_col2, gen_col3 = st.columns([1, 2, 1])
    with gen_col2:
        generate_btn = st.button(
            "🚀 GENERATE TAILORED JD & TARGET COMPANIES",
            key="generate_career_btn",
            disabled=not (user_skills_input or "").strip(),
            use_container_width=True,
        )

    st.markdown('</div>', unsafe_allow_html=True)

    if generate_btn and user_skills_input and user_skills_input.strip():
        with st.spinner("🤖 AI is analyzing your stack, target roles, and company matches..."):
            try:
                from core.feedback import generate_job_and_career_recommendations
                recommendations = generate_job_and_career_recommendations(user_skills_input)
                st.session_state.career_recommendations = recommendations
                st.toast("✅ Job & Company Recommendations Generated!", icon="🎉")
            except Exception as e:
                st.error(f"Generation failed: {str(e)}")

    if st.session_state.career_recommendations:
        rec = st.session_state.career_recommendations

        st.markdown("<hr style='border-color:rgba(138,124,248,0.25);margin:24px 0;'>", unsafe_allow_html=True)

        r_col1, r_col2 = st.columns([1, 1], gap="medium")

        # Recommended Roles & Target Companies
        with r_col1:
            st.markdown('<div class="neo-card">', unsafe_allow_html=True)
            st.markdown(
                '<p style="font-family:\'Space Grotesk\';font-size:18px;font-weight:700;margin:0 0 12px;text-align:center;">'
                '🎯 Best Matching Company Roles</p>',
                unsafe_allow_html=True,
            )
            roles = rec.get("recommended_roles", [])
            if roles:
                role_pills = '<div style="text-align:center;">' + " ".join(f'<span class="tag-pill tag-matched" style="font-size:13px;padding:8px 16px;">💼 {role}</span>' for role in roles) + '</div>'
                st.markdown(role_pills, unsafe_allow_html=True)

            st.markdown("<br><hr style='border-color:rgba(138,124,248,0.15);margin:16px 0;'><br>", unsafe_allow_html=True)

            st.markdown(
                '<p style="font-family:\'Space Grotesk\';font-size:18px;font-weight:700;margin:0 0 12px;text-align:center;">'
                '🏢 Top Hiring Target Companies</p>',
                unsafe_allow_html=True,
            )
            for comp in rec.get("target_companies", []):
                st.markdown(
                    f"""<div class="company-card">
                    <b style="font-size:15px;color:{T['accent_cyan']};">{comp.get('name','')}</b> 
                    <span style="font-size:11px;color:{T['text_muted']};">({comp.get('sector','')})</span><br>
                    <span style="font-size:12.5px;color:{T['text_main']};margin-top:4px;display:block;">
                        💡 <b>Why Match:</b> {comp.get('why_fit','')}
                    </span>
                    </div>""",
                    unsafe_allow_html=True,
                )

            st.markdown('</div>', unsafe_allow_html=True)

        # Generated Tailored JD
        with r_col2:
            st.markdown('<div class="neo-card">', unsafe_allow_html=True)
            st.markdown(
                '<p style="font-family:\'Space Grotesk\';font-size:18px;font-weight:700;margin:0 0 12px;text-align:center;">'
                '📄 Generated Tailored Job Description</p>',
                unsafe_allow_html=True,
            )
            generated_jd = rec.get("generated_job_description", "")
            st.text_area(
                label="Generated JD",
                value=generated_jd,
                height=260,
                key="display_gen_jd",
            )

            if st.button("📋 Copy JD to ATS Diagnostic Scanner", key="transfer_jd_btn", use_container_width=True):
                st.session_state.jd_input = generated_jd
                st.session_state.transferred_jd = generated_jd
                st.toast("✅ Job Description copied to ATS Scanner!", icon="📋")

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                '<p style="font-family:\'Space Grotesk\';font-size:16px;font-weight:700;margin:0 0 10px;">'
                '💡 Strategic Career Insights</p>',
                unsafe_allow_html=True,
            )
            for insight in rec.get("career_insights", []):
                st.markdown(f'<div style="font-size:13px;padding:6px 0;color:{T["text_main"]};">🚀 {insight}</div>', unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)


def render_rewriter_tab():
    st.markdown(
        """
        <div class="workbench-hero" style="text-align: center;">
            <h1 class="hero-title" style="text-align: center;">1-Click AI Resume Rewriter & ATS Exporter</h1>
            <p class="hero-subtitle" style="text-align: center; margin: 0 auto;">
                Automatically incorporate missing target skills, optimize experience bullet points with quantified metrics,
                and export an ATS-compliant PDF or editable Word document (.docx).
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="neo-card">', unsafe_allow_html=True)

    has_scanned_data = st.session_state.results is not None

    col1, col2 = st.columns([1, 1], gap="medium")
    with col1:
        st.markdown('<p style="font-family:\'Space Grotesk\';font-size:16px;font-weight:700;margin-bottom:8px;">📄 Resume Text Input</p>', unsafe_allow_html=True)
        default_res_text = st.session_state.results.get("resume_full_text", "") if has_scanned_data else ""
        rew_resume_text = st.text_area(
            label="Resume Text",
            value=default_res_text,
            height=200,
            placeholder="Paste your current resume text here (or upload a PDF in the Scanner tab)...",
            key="rew_resume_input",
        )
    with col2:
        st.markdown('<p style="font-family:\'Space Grotesk\';font-size:16px;font-weight:700;margin-bottom:8px;">🎯 Target Job Description</p>', unsafe_allow_html=True)
        default_jd_text = st.session_state.results.get("target_jd", "") if has_scanned_data else (st.session_state.transferred_jd or "")
        rew_jd_text = st.text_area(
            label="Job Description",
            value=default_jd_text,
            height=200,
            placeholder="Paste the target job description text here...",
            key="rew_jd_input",
        )

    b_col1, b_col2, b_col3 = st.columns([1, 2, 1])
    with b_col2:
        run_rewrite_btn = st.button(
            "⚡ REWRITE & OPTIMIZE RESUME WITH AI",
            key="run_rewrite_btn",
            disabled=not (rew_resume_text and rew_resume_text.strip() and rew_jd_text and rew_jd_text.strip()),
            use_container_width=True,
        )

    st.markdown('</div>', unsafe_allow_html=True)

    if run_rewrite_btn and rew_resume_text and rew_jd_text:
        with st.spinner("🤖 AI is restructuring your resume and incorporating target keywords..."):
            try:
                from core.rewriter import rewrite_resume_with_ai
                mock_score_report = st.session_state.results or {"matched_skills": [], "missing_skills": []}
                rewritten_data = rewrite_resume_with_ai(rew_resume_text, rew_jd_text, mock_score_report)
                st.session_state.rewritten_resume = rewritten_data
                st.toast("✅ Resume Successfully Rewritten & Optimized!", icon="🎉")
            except Exception as e:
                st.error(f"Rewriting failed: {str(e)}")

    if st.session_state.rewritten_resume:
        rew = st.session_state.rewritten_resume

        st.markdown("<hr style='border-color:rgba(138,124,248,0.25);margin:24px 0;'>", unsafe_allow_html=True)
        st.markdown('<div class="neo-card">', unsafe_allow_html=True)
        st.markdown(
            '<p style="font-family:\'Space Grotesk\';font-size:18px;font-weight:700;margin:0 0 16px;text-align:center;">'
            '📥 Download ATS-Compliant Documents</p>',
            unsafe_allow_html=True,
        )

        try:
            from core.exporter import export_to_pdf, export_to_docx
            pdf_bytes = export_to_pdf(rew)
            docx_bytes = export_to_docx(rew)

            d_col1, d_col2 = st.columns(2, gap="medium")
            with d_col1:
                st.download_button(
                    label="📥 Download ATS PDF Resume (.pdf)",
                    data=pdf_bytes,
                    file_name="ATS_Optimized_Resume.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    key="tab_dl_pdf_btn",
                )
            with d_col2:
                st.download_button(
                    label="📥 Download Editable Resume (.docx)",
                    data=docx_bytes,
                    file_name="ATS_Optimized_Resume.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                    key="tab_dl_docx_btn",
                )
        except Exception as exp_err:
            st.error(f"Failed to generate download files: {str(exp_err)}")

        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("📄 View Rewritten Resume Content Preview", expanded=True):
            st.markdown(f"### {rew.get('full_name', 'CANDIDATE NAME')}")
            st.markdown(f"*{rew.get('contact_info', '')}*")
            st.markdown("---")
            st.markdown(f"**Professional Summary:**\n{rew.get('professional_summary', '')}")
            st.markdown("---")
            st.markdown("**Technical Skills Matrix:**")
            for cat, sk_l in rew.get("technical_skills", {}).items():
                sk_str = ", ".join(sk_l) if isinstance(sk_l, list) else str(sk_l)
                st.markdown(f"- **{cat}:** {sk_str}")
            st.markdown("---")
            st.markdown("**Optimized Experience Bullets:**")
            for exp in rew.get("work_experience", []):
                st.markdown(f"**{exp.get('title','')} | {exp.get('company','')}** *({exp.get('location_dates','')})*")
                for b in exp.get("bullet_points", []):
                    st.markdown(f"• {b}")

        st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────
# Main Execution Loop
# ─────────────────────────────────────────────────────────
def main():
    inject_custom_styles()
    render_header()

    main_tab1, main_tab2, main_tab3 = st.tabs([
        "⚡ RESUME ATS DIAGNOSTIC SCANNER",
        "🚀 AI JOB & TARGET COMPANY GENERATOR",
        "✨ 1-CLICK AI RESUME REWRITER & EXPORTER",
    ])

    with main_tab1:
        uploaded_file, jd_text, analyze_btn = render_ats_scanner_tab()

        if analyze_btn and uploaded_file and jd_text and jd_text.strip():
            file_bytes = uploaded_file.getvalue()
            filename = uploaded_file.name
            target_jd = jd_text

            progress_placeholder = st.empty()
            status_placeholder = st.empty()

            progress_bar = progress_placeholder.progress(0)

            status_placeholder.markdown(
                f'<div style="text-align:center;font-size:14px;color:{T["accent_cyan"]};padding:14px;font-weight:700;">'
                f'⚡ Executing Hybrid Vector Scan...</div>',
                unsafe_allow_html=True,
            )
            progress_bar.progress(0.45)
            time.sleep(0.3)

            try:
                from core.scorer import compute_ats_score
                from core.feedback import generate_feedback

                results = compute_ats_score(file_bytes, filename, target_jd)
                st.session_state.results = results
                st.session_state.rewritten_resume = None

                status_placeholder.markdown(
                    f'<div style="text-align:center;font-size:14px;color:{T["accent_pink"]};padding:14px;font-weight:700;">'
                    f'🤖 Generating AI Feedback & Coaching Recommendations...</div>',
                    unsafe_allow_html=True,
                )
                progress_bar.progress(0.85)

                feedback = generate_feedback(
                    results["resume_full_text"], target_jd, results
                )
                st.session_state.feedback = feedback

                progress_bar.progress(1.0)
                status_placeholder.markdown(
                    f'<div style="text-align:center;font-size:14px;color:{T["accent_emerald"]};padding:14px;font-weight:800;">'
                    f'✅ Scan Complete!</div>',
                    unsafe_allow_html=True,
                )
                time.sleep(0.4)

            except Exception as e:
                status_placeholder.error(f"Analysis failed: {str(e)}")
                st.exception(e)
                st.stop()

            progress_placeholder.empty()
            status_placeholder.empty()

        if st.session_state.results:
            st.markdown("<hr style='border-color:rgba(138,124,248,0.25);margin:28px 0;'>", unsafe_allow_html=True)
            render_dashboard(st.session_state.results, st.session_state.feedback)

    with main_tab2:
        render_career_generator_tab()

    with main_tab3:
        render_rewriter_tab()


if __name__ == "__main__":
    main()
