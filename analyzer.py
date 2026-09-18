"""
AI Analysis Engine using Google Gemini.
Handles prompt construction, API call execution, and response parsing/validation.
"""
import os
import json
import re
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()


class AnalysisError(Exception):
    """Base exception for analysis engine errors."""
    pass


class MissingAPIKeyError(AnalysisError):
    """Raised when GEMINI_API_KEY is missing or empty."""
    pass


class APICommunicationError(AnalysisError):
    """Raised when Gemini API request fails or times out."""
    pass


class ResponseParsingError(AnalysisError):
    """Raised when model response cannot be parsed or sanitized into valid JSON."""
    pass


def clean_json_response(raw_text: str) -> str:
    """
    Strips markdown code fences (```json ... ```) and leading/trailing whitespace.
    """
    text = raw_text.strip()
    fence_pattern = r"^```(?:json)?\s*(.*?)\s*```$"
    match = re.search(fence_pattern, text, re.DOTALL | re.IGNORECASE)
    if match:
        text = match.group(1).strip()
    return text


def sanitize_and_validate_analysis(parsed_data: dict) -> dict:
    """
    Validates and cleanses the parsed JSON object against the required schema,
    ensuring safe defaults and clamping match_score to 0-100.
    """
    if not isinstance(parsed_data, dict):
        raise ResponseParsingError("Parsed AI response is not a valid JSON object.")

    # 1. match_score
    score_raw = parsed_data.get("match_score", 0)
    try:
        score = int(round(float(score_raw)))
    except (ValueError, TypeError):
        score = 0
    score = max(0, min(100, score))

    # Helper for list fields
    def safe_string_list(key: str) -> list[str]:
        val = parsed_data.get(key, [])
        if isinstance(val, list):
            return [str(item).strip() for item in val if item is not None and str(item).strip()]
        elif isinstance(val, str) and val.strip():
            return [val.strip()]
        return []

    # 2. summary string
    summary_val = parsed_data.get("summary", "No summary provided.")
    summary = str(summary_val).strip() if summary_val else "No summary provided."

    return {
        "match_score": score,
        "matching_skills": safe_string_list("matching_skills"),
        "missing_skills": safe_string_list("missing_skills"),
        "experience_alignment": safe_string_list("experience_alignment"),
        "weaknesses": safe_string_list("weaknesses"),
        "improvements": safe_string_list("improvements"),
        "summary": summary,
    }


def analyze_resume(resume_text: str, job_description: str) -> dict:
    """
    Analyze resume against a job description using Google Gemini LLM.

    Args:
        resume_text (str): Plain text content of the resume.
        job_description (str): Plain text content of the job description.

    Returns:
        dict: Validated analysis dictionary matching the required schema.

    Raises:
        MissingAPIKeyError: If GEMINI_API_KEY environment variable is not configured.
        APICommunicationError: If API call fails or hits rate limits.
        ResponseParsingError: If response is malformed and cannot be parsed.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or not api_key.strip():
        raise MissingAPIKeyError("API key not configured. Please set GEMINI_API_KEY in your .env file.")

    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        raise APICommunicationError(f"Failed to configure Gemini API client: {str(e)}") from e

    prompt = f"""
You are an expert technical recruiter and resume analyst. Analyze the candidate resume against the job description.

Compare the resume text against the job description and evaluate candidate fit, technical skills, experience alignment, key weaknesses, actionable improvements, and a concise recruiter summary.

STRICT INSTRUCTIONS:
- You MUST return STRICT JSON ONLY.
- Do NOT wrap your output in markdown backticks or commentary outside the JSON.
- Your JSON output MUST match this exact schema:
{{
  "match_score": <integer from 0 to 100 representing overall fit>,
  "matching_skills": [<array of skill strings found in both resume and job description>],
  "missing_skills": [<array of skill strings required by job description but missing in resume>],
  "experience_alignment": [<array of bullet strings mapping resume experience to JD requirements>],
  "weaknesses": [<array of bullet strings highlighting candidate weak points relative to job description>],
  "improvements": [<array of actionable recommendation bullet strings for the candidate>],
  "summary": "<3 to 5 sentence natural language summary of candidate fit>"
}}

--- RESUME TEXT ---
{resume_text}

--- JOB DESCRIPTION ---
{job_description}
"""

    generation_config = {
        "response_mime_type": "application/json",
        "temperature": 0.2,
    }

    model_name = "gemini-3.6-flash"

    try:
        model = genai.GenerativeModel(model_name=model_name, generation_config=generation_config)
        response = model.generate_content(prompt)
    except Exception as e:
        err_str = str(e).lower()
        if "429" in err_str or "resource_exhausted" in err_str or "quota" in err_str or "rate limit" in err_str:
            raise APICommunicationError("Too many requests — please wait a moment and try again.") from e
        elif "401" in err_str or "api_key" in err_str or "invalid" in err_str:
            raise APICommunicationError("API key not configured correctly or invalid. Please check your .env file.") from e
        else:
            raise APICommunicationError(f"Analysis service is unavailable right now. ({str(e)})") from e

    raw_response = getattr(response, "text", "")
    if not raw_response:
        raise ResponseParsingError("Received empty response from AI analysis model.")

    cleaned_text = clean_json_response(raw_response)

    try:
        parsed_json = json.loads(cleaned_text)
    except json.JSONDecodeError as e:
        raise ResponseParsingError(f"Couldn't parse the AI's response into JSON. ({str(e)})") from e

    return sanitize_and_validate_analysis(parsed_json)
