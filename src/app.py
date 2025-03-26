"""
SoCa (Submission over Criteria) Analysis Tool - Main Application Entry Point

A Streamlit-based application that analyzes multiple submission documents
using a sophisticated AI model, providing detailed feedback and comparison
tools for evaluation processes.
"""

import streamlit as st
from config import configure_page
from services import extract_text_from_file
from ui.main_page import process_submissions, display_results
from ui.sidebar import render_sidebar
from utils.helpers import convert_text_to_job_criteria_json, update_job_criteria_in_azure


def main():
    """Main application entry point."""
    configure_page()

    st.title("📄 SoCa: Submission over Criteria")
    st.markdown("*AI-powered submission analysis and evaluation*")

    # Initialize session state if not exists
    if 'analysis_completed' not in st.session_state:
        st.session_state['analysis_completed'] = False
        st.session_state['results'] = []
        st.session_state['thread_ids'] = []

    uploaded_files, process_button = render_sidebar()

    # Main content area
    if not uploaded_files:
        st.info(
            "Please upload one or more submission files from the sidebar to begin analysis.")

        with st.expander("View Example Analysis"):
            st.markdown("""
            ### Example Submission Analysis Result
            
            #### Evaluation Report

            ### Overall Summary:
            John Smith's qualifications and extensive experience in software development make him a strong candidate for positions related to web development. His demonstrated expertise in Python, JavaScript, and React highlights his suitability for roles requiring these technical skills.

            ### Detailed Evaluation:

            #### Technical Skills
            John has strong experience with Python, JavaScript, and React, which are key requirements for the role. His background includes building RESTful APIs using Flask and implementing front-end features with JavaScript.

            #### Experience
            John has 7 years of experience in software development, exceeding the minimum requirement of 3 years. He has held senior positions and led a team of junior developers.

            #### Education
            John holds a Bachelor's degree in Computer Science from the University of Technology, meeting the educational requirement for the position.

            #### Communication Skills
            John's submission is well-written with clear descriptions of his responsibilities and achievements, indicating good written communication skills.

            ### Scoring:

            | Criteria | Score (1-5) | Comment |
            |---------------------------|-------------|---------|
            | Technical Skills | 5 | Strong experience in all required technologies. |
            | Experience | 5 | Exceeds required years of experience and has leadership experience. |
            | Education | 5 | Holds relevant degree in Computer Science. |
            | Communication Skills | 4 | Well-written submission demonstrates good communication ability. |

            """)

    elif process_button or st.session_state.get('analysis_completed'):
        # Process submissions if button was clicked or we already have results
        if not st.session_state['analysis_completed'] and process_button:
            results = process_submissions(uploaded_files)

            st.session_state['results'] = results
            st.session_state['thread_ids'] = [
                r.get("Thread ID", "") for r in results]
            st.session_state['analysis_completed'] = True

        display_results(st.session_state.get('results', []))


if __name__ == "__main__":
    main()
