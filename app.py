import streamlit as st
from utils import (
    extract_text_from_pdf,
    sanitize_job_description,
    validate_inputs,
    PDFExtractionError,
    EmptyPDFError,
)
from analyzer import (
    analyze_resume,
    MissingAPIKeyError,
    APICommunicationError,
    ResponseParsingError,
    AnalysisError,
)
from style import inject_custom_css, render_skill_pills, render_summary_box

# Configure Page Layout
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

# Inject Custom CSS Theme
inject_custom_css()

# Header Section
st.title("📄 AI Resume Analyzer")
st.markdown('<div class="app-subtitle">Upload your resume and paste a job description to receive an instant, explainable AI-powered match analysis.</div>', unsafe_allow_html=True)

# Input Section (Two Columns)
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("1. Candidate Resume")
    uploaded_file = st.file_uploader("Upload Resume (PDF format)", type=["pdf"])
    if uploaded_file:
        file_size_kb = round(uploaded_file.size / 1024, 1)
        st.markdown(
            f'<div class="status-badge badge-success">✓ Resume loaded: <strong>{uploaded_file.name}</strong> ({file_size_kb} KB)</div>',
            unsafe_allow_html=True,
        )

with col_right:
    st.subheader("2. Job Description")
    job_description_input = st.text_area(
        "Paste Job Description",
        height=210,
        placeholder="Paste requirements, qualifications, and role responsibilities here...",
    )
    if job_description_input and job_description_input.strip():
        word_count = len(job_description_input.strip().split())
        char_count = len(job_description_input.strip())
        st.markdown(
            f'<div class="status-badge badge-info">📝 Job description ready ({word_count} words / {char_count} chars)</div>',
            unsafe_allow_html=True,
        )

# Validation check for button state
has_resume = uploaded_file is not None
has_jd = bool(job_description_input and job_description_input.strip())
is_ready = has_resume and has_jd

st.write("")  # Spacing
btn_col1, btn_col2 = st.columns([1, 3])

with btn_col1:
    analyze_clicked = st.button("🔍 Analyze Resume", type="primary", disabled=not is_ready, use_container_width=True)

with btn_col2:
    if not is_ready:
        missing_parts = []
        if not has_resume:
            missing_parts.append("resume PDF")
        if not has_jd:
            missing_parts.append("job description")
        missing_str = " and ".join(missing_parts)
        st.caption(f"ℹ️ Please provide a {missing_str} above to activate analysis.")

# Process Analysis Action
if analyze_clicked:
    is_valid, err_msg = validate_inputs(uploaded_file, job_description_input)
    if not is_valid:
        st.error(err_msg)
    else:
        try:
            with st.status("🔍 Analyzing Resume Fit with Gemini AI...", expanded=True) as status:
                status.update(label="Reading & extracting resume text...", state="running")
                resume_text, is_resume_truncated = extract_text_from_pdf(uploaded_file)
                job_description, is_jd_truncated = sanitize_job_description(job_description_input)

                if is_resume_truncated or is_jd_truncated:
                    truncated_sources = []
                    if is_resume_truncated:
                        truncated_sources.append("resume text")
                    if is_jd_truncated:
                        truncated_sources.append("job description")
                    sources_str = " and ".join(truncated_sources)
                    st.warning(f"Notice: The {sources_str} exceeded 6,000 characters and was truncated for analysis.")

                status.update(label="Comparing resume skills and experience against job description...", state="running")
                analysis_result = analyze_resume(resume_text, job_description)

                status.update(label="Finalizing recruiter summary and score...", state="running")
                st.session_state["analysis_result"] = analysis_result
                status.update(label="Analysis complete!", state="complete", expanded=False)

            st.toast("🎉 Analysis complete!", icon="🎉")
            st.rerun()

        except PDFExtractionError:
            st.error("Could not read this PDF. Please upload a valid PDF file.")
        except EmptyPDFError:
            st.error("No text could be extracted from this resume. Try a text-based PDF (not a scanned image).")
        except MissingAPIKeyError as e:
            st.error(str(e))
        except APICommunicationError as e:
            st.error(str(e))
        except ResponseParsingError as e:
            st.error(str(e))
        except AnalysisError as e:
            st.error(f"Analysis failed: {str(e)}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {str(e)}")

# Results Dashboard View
if "analysis_result" in st.session_state:
    result = st.session_state["analysis_result"]

    st.divider()

    # Dashboard Header & Reset Option
    header_col1, header_col2 = st.columns([3, 1])
    with header_col1:
        st.header("📊 Candidate Evaluation Dashboard")
    with header_col2:
        if st.button("🔄 Analyze Another Resume / JD", type="secondary", use_container_width=True):
            del st.session_state["analysis_result"]
            st.rerun()

    # Organized Tabbed View
    tab_overview, tab_skills, tab_exp_gaps, tab_suggestions = st.tabs([
        "📊 Overview & Fit Score",
        "⚡ Skills Breakdown",
        "🎯 Experience & Weaknesses",
        "💡 Recommendations & Summary",
    ])

    # TAB 1: OVERVIEW & FIT SCORE
    with tab_overview:
        score = result.get("match_score", 0)

        # Determine Score Color Theme
        if score >= 75:
            score_color = "#34d399"  # Green
            score_label = "Strong Match"
        elif score >= 50:
            score_color = "#fbbf24"  # Amber
            score_label = "Moderate Fit"
        else:
            score_color = "#f87171"  # Red
            score_label = "Low Alignment"

        card_col1, card_col2 = st.columns([1, 2])
        with card_col1:
            st.markdown(
                f"""
                <div class="score-card">
                    <div>
                        <div class="score-label">Overall Fit Score</div>
                        <div class="score-value" style="color: {score_color};">{score}<span style="font-size: 1.5rem; color: #64748b;">/100</span></div>
                    </div>
                    <div style="font-size: 1.1rem; font-weight: 700; color: {score_color};">{score_label}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with card_col2:
            st.write("")
            st.progress(score / 100.0)
            matching_cnt = len(result.get("matching_skills", []))
            missing_cnt = len(result.get("missing_skills", []))
            st.caption(f"📈 Quick Insights: Identified **{matching_cnt}** matching skills and **{missing_cnt}** skill gaps relative to the job description.")

        st.caption("⚠️ Disclaimer: This match score is an AI-generated heuristic intended for guidance only, not a validated hiring decision score.")

    # TAB 2: SKILLS BREAKDOWN
    with tab_skills:
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.subheader("✅ Matching Candidate Skills")
            render_skill_pills(result.get("matching_skills", []), is_match=True)

        with col_m2:
            st.subheader("❌ Missing / Required Job Skills")
            render_skill_pills(result.get("missing_skills", []), is_match=False)

    # TAB 3: EXPERIENCE & WEAKNESSES
    with tab_exp_gaps:
        col_e1, col_e2 = st.columns(2)

        with col_e1:
            st.subheader("🎯 Experience Alignment")
            exp_items = result.get("experience_alignment", [])
            if exp_items:
                for item in exp_items:
                    st.markdown(f"- {item}")
            else:
                st.write("No specific experience alignment points returned.")

        with col_e2:
            st.subheader("⚠️ Candidate Weaknesses & Gaps")
            weaknesses = result.get("weaknesses", [])
            if weaknesses:
                for item in weaknesses:
                    st.markdown(f"- {item}")
            else:
                st.write("No major weaknesses identified.")

    # TAB 4: RECOMMENDATIONS & SUMMARY
    with tab_suggestions:
        # Recruiter Summary Box
        render_summary_box(result.get("summary", "No summary provided."))

        st.subheader("💡 Actionable Improvement Suggestions")
        improvements = result.get("improvements", [])
        if improvements:
            for item in improvements:
                st.markdown(f"💡 {item}")
        else:
            st.write("No specific improvements suggested.")
