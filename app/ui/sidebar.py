"""
Sidebar UI components for the CV Analysis Tool.
"""

import streamlit as st
import pandas as pd
import json
from typing import Dict, Any, Tuple, List, Optional

from services import extract_text_from_file
from utils.helpers import convert_text_to_job_criteria_json, update_job_criteria_in_azure


def render_sidebar():
    """Render the sidebar UI components and handle sidebar interactions."""
    st.sidebar.header("Upload CVs")

    # Multi-file uploader for CVs
    uploaded_files = st.sidebar.file_uploader(
        "Upload CV files (PDF, DOCX, TXT)",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
        key="cv_files"
    )

    # Job Criteria Configuration Section
    st.sidebar.markdown("### ⚙️ Job Criteria Configuration")
    st.sidebar.markdown("""
    **Update Job Criteria**
    
    Upload a job description document to update the criteria used for evaluating CVs.
    """)

    job_criteria_file = st.sidebar.file_uploader(
        "Upload Job Criteria Document (PDF, DOCX)",
        type=["pdf", "docx"],
        key="job_criteria_file"
    )

    if job_criteria_file:
        # Extract text from the uploaded file
        job_text = extract_text_from_file(job_criteria_file)

        # Setup tabs for previewing content
        preview_tabs = st.sidebar.tabs(["Extracted Text", "Generated JSON"])

        with preview_tabs[0]:
            st.text_area("Extracted Text from Document",
                         job_text, height=200)

        # Convert to JSON
        job_criteria = convert_text_to_job_criteria_json(job_text)

        with preview_tabs[1]:
            st.json(job_criteria)

        # Update button
        if st.sidebar.button("Update Job Criteria", key="update_criteria"):
            with st.spinner("Updating job criteria..."):
                if update_job_criteria_in_azure(job_criteria):
                    st.sidebar.success("Job criteria updated successfully!")
                else:
                    st.sidebar.error(
                        "Failed to update job criteria. Check logs for details.")

    st.sidebar.markdown("---")

    # Note about the application
    st.sidebar.subheader("About This Application")
    st.sidebar.text(
        "This application analyzes CVs using an AI model, "
        "providing comprehensive evaluations with scorecards, "
        "detailed assessments, and comparative summaries. "
        "It delivers structured insights including position fit, "
        "candidate qualification scores, and specific recommendations."
    )

    # Note about criteria
    st.sidebar.subheader("Evaluation Criteria")
    st.sidebar.text(
        "Each CV is evaluated against position requirements "
        "with numerical scoring and detailed feedback across "
        "key categories. The comparative summary tab uses "
        "Azure OpenAI to provide side-by-side candidate "
        "comparisons to help with hiring decisions."
    )

    # Process button
    process_button = st.sidebar.button("Analyze CVs", type="primary")

    # Export results button
    if st.session_state.get('analysis_completed'):
        export_results = st.sidebar.download_button(
            label="Export Results as CSV",
            data=pd.DataFrame(st.session_state.get(
                'results', [])).to_csv(index=False),
            file_name="cv_analysis_results.csv",
            mime="text/csv"
        )

        # Add clear results button
        if st.sidebar.button("Clear Results", type="secondary"):
            st.session_state['analysis_completed'] = False
            st.session_state['results'] = []
            st.session_state['thread_ids'] = []
            st.rerun()

    return uploaded_files, process_button
