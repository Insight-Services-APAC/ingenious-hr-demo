"""
Sidebar UI components for the SoCa (Submission over Criteria) Analysis Tool.
"""

import streamlit as st
import pandas as pd
import json
from typing import Dict, Any, Tuple, List, Optional

from services import extract_text_from_file
from utils.helpers import convert_text_to_job_criteria_json, update_job_criteria_in_azure


def render_sidebar():
    """Render the sidebar UI components and handle sidebar interactions."""
    # Main functionality section at the top
    st.sidebar.header("SoCa: Submission over Criteria")
    st.sidebar.markdown("*A demonstration of AI-powered submission analysis*")

    # Submission Upload
    uploaded_files = st.sidebar.file_uploader(
        "Upload Submissions (PDF, DOCX, TXT)",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
        key="cv_files"
    )

    # Criteria Configuration
    st.sidebar.markdown("### Criteria Configuration")

    job_criteria_file = st.sidebar.file_uploader(
        "Upload Criteria Document (PDF, DOCX)",
        type=["pdf", "docx"],
        key="job_criteria_file"
    )

    if job_criteria_file:
        job_text = extract_text_from_file(job_criteria_file)
        job_criteria = convert_text_to_job_criteria_json(job_text)

        if st.sidebar.button("Update Criteria", key="update_criteria"):
            with st.spinner("Updating criteria..."):
                if update_job_criteria_in_azure(job_criteria):
                    st.sidebar.success("Criteria updated successfully!")
                else:
                    st.sidebar.error(
                        "Failed to update criteria. Check logs for details.")

    # Analyze button positioned right after uploads
    process_button = st.sidebar.button("Analyze Submissions", type="primary")

    # Export/Clear results buttons if analysis is completed
    if st.session_state.get('analysis_completed'):
        export_results = st.sidebar.download_button(
            label="Export Results as CSV",
            data=pd.DataFrame(st.session_state.get(
                'results', [])).to_csv(index=False),
            file_name="submission_analysis_results.csv",
            mime="text/csv"
        )

        if st.sidebar.button("Clear Results", type="secondary"):
            st.session_state['analysis_completed'] = False
            st.session_state['results'] = []
            st.session_state['thread_ids'] = []
            st.rerun()

    # Separator before information section
    st.sidebar.markdown("---")

    st.sidebar.subheader("About SoCa")
    st.sidebar.markdown(
        "SoCa (Submission over Criteria) is an app template that "
        "can be deployed for various use cases where submissions "
        "need to be evaluated against specific criteria."
    )

    st.sidebar.text(
        "This demonstration analyzes submissions using an AI model, "
        "providing comprehensive evaluations with scorecards, "
        "detailed assessments, and comparative analysis. "
        "It delivers structured insights related to the criteria fit "
        "and specific recommendations."
    )

    return uploaded_files, process_button
