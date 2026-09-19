"""
Utility functions for file handling, text extraction, and validation.
"""
import pymupdf as fitz  # PyMuPDF

MAX_CHARACTERS = 6000


class PDFExtractionError(Exception):
    """Custom exception raised when PDF extraction fails or file is corrupt."""
    pass


class EmptyPDFError(Exception):
    """Custom exception raised when PDF has no extractable text."""
    pass


def extract_text_from_pdf(uploaded_file) -> tuple[str, bool]:
    """
    Extract text content from an uploaded PDF file using PyMuPDF.

    Args:
        uploaded_file: Streamlit UploadedFile object or file-like object.

    Returns:
        tuple[str, bool]: (extracted_text, is_truncated)

    Raises:
        PDFExtractionError: If the file is corrupt or cannot be opened/read as PDF.
        EmptyPDFError: If the PDF contains no extractable text (e.g., scanned image).
    """
    try:
        if hasattr(uploaded_file, "getvalue"):
            pdf_bytes = uploaded_file.getvalue()
        else:
            pdf_bytes = uploaded_file.read()

        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    except Exception as e:
        raise PDFExtractionError(f"Failed to open or read PDF file: {str(e)}") from e

    try:
        text_pages = []
        for page in doc:
            text = page.get_text()
            if text:
                text_pages.append(text)
        doc.close()
    except Exception as e:
        raise PDFExtractionError(f"Error extracting text from PDF pages: {str(e)}") from e

    extracted_text = "\n".join(text_pages).strip()

    if not extracted_text:
        raise EmptyPDFError("No extractable text found in PDF.")

    is_truncated = False
    if len(extracted_text) > MAX_CHARACTERS:
        extracted_text = extracted_text[:MAX_CHARACTERS]
        is_truncated = True

    return extracted_text, is_truncated


def sanitize_job_description(job_description: str) -> tuple[str, bool]:
    """
    Sanitize and truncate job description to safe token boundary.

    Args:
        job_description (str): Raw job description input.

    Returns:
        tuple[str, bool]: (sanitized_jd_text, is_truncated)
    """
    cleaned_jd = job_description.strip() if job_description else ""
    is_truncated = False
    if len(cleaned_jd) > MAX_CHARACTERS:
        cleaned_jd = cleaned_jd[:MAX_CHARACTERS]
        is_truncated = True
    return cleaned_jd, is_truncated


def validate_inputs(uploaded_file, job_description: str) -> tuple[bool, str]:
    """
    Validate presence of required inputs before processing.

    Args:
        uploaded_file: Uploaded file object or None.
        job_description (str): Job description text.

    Returns:
        tuple[bool, str]: (is_valid, error_message)
    """
    if uploaded_file is None:
        return False, "Please upload a resume PDF."

    if not job_description or not job_description.strip():
        return False, "Please paste a job description."

    return True, ""
