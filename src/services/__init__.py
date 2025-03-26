"""
Services package for the SoCa (Submission over Criteria) Analysis Tool.
Contains modules for API communication, blob storage, and text extraction.
"""

from services.api_client import APIClient
from services.text_extraction import (
    extract_text_from_file,
    extract_text_from_pdf,
    extract_text_from_docx
)
from services.openai_client import summarize_submission_analyses, generate_followup_questions

__all__ = [
    'APIClient',
    'extract_text_from_file',
    'extract_text_from_pdf',
    'extract_text_from_docx',
    'summarize_submission_analyses',
    'generate_followup_questions'
]
