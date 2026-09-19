# AI Resume Analyzer

AI Resume Analyzer is a lightweight, single-page Streamlit web application that evaluates candidate resume PDFs against job descriptions using Google Gemini AI. The tool delivers a structured, explainable match analysis—including a fit score, matching and missing skills, experience alignment points, candidate weaknesses, actionable improvement recommendations, and a recruiter-style summary.

---

## Features

- **PDF Resume Text Extraction**: Extracts text directly from uploaded PDF resumes using PyMuPDF (`pymupdf`).
- **Structured AI Evaluation**: Uses Google Gemini's native JSON mode to generate structured analysis matching a strict JSON schema.
- **Explainable Match Score**: Displays an overall fit score (0–100) with visual progress feedback and heuristic disclaimers.
- **Skill Gap Analysis**: Compares candidate skills against job requirements in a side-by-side view (matching skills vs. missing skills).
- **Experience Alignment**: Highlights specific points where candidate experience aligns with job description requirements.
- **Weaknesses & Improvement Suggestions**: Identifies resume gaps and provides concrete recommendations for improvement.
- **Recruiter Summary**: Generates a natural-language synthesis summarizing overall candidate fit.
- **Robust Validation & Error Handling**: Surface non-technical feedback for empty inputs, corrupt PDFs, non-text (scanned) PDFs, missing API keys, rate limits, or API communication errors.
- **Safe Input Bounding**: Truncates excessively long resumes or job descriptions (>6,000 characters) to remain within token limits.

---

## Architecture

The project follows a clean, single-page Streamlit architecture separated into UI, text extraction utilities, and the Gemini AI engine:

```text
               ┌────────────────────────────────────────┐
               │         Streamlit Web UI               │
               │               (app.py)                 │
               └───────────────────┬────────────────────┘
                                   │
                 ┌─────────────────┴─────────────────┐
                 ▼                                   ▼
   ┌───────────────────────────┐       ┌───────────────────────────┐
   │    PDF & Text Utilities   │       │    AI Analysis Engine     │
   │        (utils.py)         │       │       (analyzer.py)       │
   │                           │       │                           │
   │  - PDF Text Extraction    │       │  - Prompt Engineering     │
   │  - Input Validation       │       │  - Gemini API JSON Mode   │
   │  - Text Truncation        │       │  - Schema Validation      │
   └───────────────────────────┘       └─────────────┬─────────────┘
                                                     │
                                                     ▼
                                       ┌───────────────────────────┐
                                       │     Google Gemini API     │
                                       │     (gemini-3.6-flash)    │
                                       └───────────────────────────┘
```

---

## Tech Stack

- **Frontend & Web Framework**: [Streamlit](https://streamlit.io/)
- **PDF Extraction**: [PyMuPDF](https://pymupdf.readthedocs.io/) (`pymupdf`)
- **LLM Engine**: [Google Gemini SDK](https://github.com/google-gemini/deprecated-generative-ai-python) (`google-generativeai`) using `gemini-3.6-flash`
- **Environment Management**: [python-dotenv](https://github.com/theskumar/python-dotenv)
- **Language**: Python 3.11+

---

## How It Works

1. **Upload & Input**: The user uploads a resume in PDF format and pastes a target job description.
2. **Extraction & Validation**: `utils.py` validates the input presence, parses text from the PDF using PyMuPDF, and truncates text if it exceeds 6,000 characters.
3. **Prompting & LLM Request**: `analyzer.py` constructs a structured recruiter prompt and invokes the Gemini API using native JSON output mode (`response_mime_type="application/json"`).
4. **Parsing & Sanitization**: The raw JSON output is sanitized, ensuring `match_score` is clamped between 0 and 100, string arrays are validated, and fallback defaults are applied if fields are missing.
5. **Dashboard Rendering**: `app.py` renders the results in an interactive, organized dashboard.

---

## Installation Steps

### Prerequisites
- Python 3.11 or higher installed on your machine.
- A valid Google Gemini API Key.

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/ai-resume-analyzer.git
cd ai-resume-analyzer
```

### 2. Create and Activate a Virtual Environment
- **Windows (PowerShell)**:
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
- **macOS / Linux**:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## Environment Setup

Create a `.env` file in the project root directory (you can copy `.env.example` as a template):

```bash
cp .env.example .env
```

Open `.env` and insert your Gemini API Key:

```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

> **Security Note:** Never commit your `.env` file or API key to version control. `.env` is listed in `.gitignore`.

---

## Usage Instructions

1. Start the Streamlit application:
   ```bash
   streamlit run app.py
   ```
2. Open your browser at `http://localhost:8501`.
3. Upload your PDF resume file.
4. Paste the job description text into the text area.
5. Click **Analyze Resume**.
6. View the generated fit score, recruiter summary, skill breakdown, experience alignment, and improvement suggestions.

---

## Example Workflow

1. **Sample File Available**: An anonymized test resume is provided at `sample/sample_resume.pdf`.
2. **Sample Job Description**:
   ```text
   Software Engineer (Python / API Development)
   Requirements:
   - Strong Python and SQL fundamentals
   - Experience building REST APIs with FastAPI or Flask
   - Experience with Docker and relational databases (PostgreSQL)
   - Cloud familiarity (AWS or GCP)
   ```
3. **Execution Output**:
   - **Match Score**: `78 / 100`
   - **Matching Skills**: Python, SQL, REST APIs, FastAPI, Docker, PostgreSQL
   - **Missing Skills**: AWS, GCP
   - **Recruiter Summary**: Detailed 3–5 sentence evaluation highlighting candidate strengths and cloud exposure gap.

---

## Screenshots Placeholder

*(Include application screenshots here after deployment or local demo runs)*

```
[ Upload & Input Interface ] ──> [ Processing Spinner ] ──> [ Results Dashboard ]
```

---

## Limitations

- **MVP Heuristic Tool**: This application is an educational MVP heuristic tool designed for candidate self-assessment. It is **not** a validated or definitive ATS (Applicant Tracking System) hiring decision tool.
- **PDF Format Only**: Supports standard text-based PDF resumes in v1. Scanned image-based PDFs without OCR text layers are not supported.
- **Document Length**: Resume text and job descriptions exceeding 6,000 characters are automatically truncated before sending to the LLM.

---

## Future Improvements

- Support for DOCX and plain text (`.txt`) file formats.
- Embeddings-based semantic retrieval for longer resumes and multi-page documents.
- PDF report export functionality for saving analysis results.
- Multi-job description comparison to compare a resume against multiple roles simultaneously.

---

## License

This project is open-source software licensed under the [MIT License](LICENSE).
