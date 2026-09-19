"""
Custom CSS styling and HTML generators for AI Resume Analyzer UI/UX upgrade.
"""
import streamlit as st


def inject_custom_css():
    """Inject custom modern theme styles into Streamlit."""
    custom_css = """
    <style>
    /* Main container padding */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }

    /* Subtitle styling */
    .app-subtitle {
        color: #94a3b8;
        font-size: 1.1rem;
        margin-bottom: 1.5rem;
    }

    /* Badge container */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.3rem 0.75rem;
        border-radius: 8px;
        font-size: 0.85rem;
        font-weight: 500;
        margin-top: 0.4rem;
    }

    .badge-success {
        background-color: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }

    .badge-info {
        background-color: rgba(59, 130, 246, 0.15);
        color: #60a5fa;
        border: 1px solid rgba(59, 130, 246, 0.3);
    }

    /* Skill pill tags */
    .skill-pill-container {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-top: 0.5rem;
        margin-bottom: 1rem;
    }

    .skill-pill {
        display: inline-block;
        padding: 0.35rem 0.8rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 500;
        letter-spacing: 0.01em;
    }

    .skill-pill-match {
        background-color: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.35);
    }

    .skill-pill-missing {
        background-color: rgba(239, 68, 68, 0.15);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.35);
    }

    /* Recruiter Summary Card */
    .summary-card {
        background-color: rgba(30, 41, 59, 0.6);
        border-left: 4px solid #3b82f6;
        border-radius: 0 10px 10px 0;
        padding: 1.25rem 1.5rem;
        margin-top: 0.75rem;
        margin-bottom: 1.5rem;
        font-size: 1.02rem;
        line-height: 1.65;
        color: #e2e8f0;
    }

    /* Score gauge container */
    .score-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.25rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    .score-value {
        font-size: 3.2rem;
        font-weight: 800;
        line-height: 1;
    }

    .score-label {
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94a3b8;
        font-weight: 600;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)


def render_skill_pills(skills: list[str], is_match: bool = True):
    """Render list of skills as colored pill tags."""
    if not skills:
        st.write("None identified.")
        return

    pill_class = "skill-pill-match" if is_match else "skill-pill-missing"
    pills_html = "".join([f'<span class="skill-pill {pill_class}">{skill}</span>' for skill in skills])
    st.markdown(f'<div class="skill-pill-container">{pills_html}</div>', unsafe_allow_html=True)


def render_summary_box(summary_text: str):
    """Render recruiter summary in a highlighted quote callout card."""
    safe_text = summary_text.replace("<", "&lt;").replace(">", "&gt;")
    st.markdown(
        f'<div class="summary-card"><strong>📝 Recruiter Synthesis:</strong><br>{safe_text}</div>',
        unsafe_allow_html=True,
    )
