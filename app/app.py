"""
CV Analysis Tool - Main Application Entry Point

A Streamlit-based application that analyzes multiple CV/resume documents
using a sophisticated AI model, providing detailed feedback and comparison
tools for recruitment processes.
"""

import streamlit as st

# Import configuration
from config import configure_page

# Import services
from services import extract_text_from_file

# Import UI components
from ui.main_page import process_cvs, display_results
from ui.sidebar import render_sidebar

# Import utilities
from utils.helpers import convert_text_to_job_criteria_json, update_job_criteria_in_azure


def main():
    """Main application entry point."""
    # Configure Streamlit page
    configure_page()

    # Display the application title
    st.title("📄 CV Analysis Tool")

    # Initialize session state if not exists
    if 'analysis_completed' not in st.session_state:
        st.session_state['analysis_completed'] = False
        st.session_state['results'] = []
        st.session_state['thread_ids'] = []

    # Render sidebar and get user inputs
    uploaded_files, process_button = render_sidebar()

    # Main content area
    if not uploaded_files:
        st.info(
            "Please upload one or more CV files from the sidebar to begin analysis.")

        # Show example
        with st.expander("View Example Analysis"):
            st.markdown("""
            ### Example CV Analysis Result
            
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
            John's CV is well-written with clear descriptions of his responsibilities and achievements, indicating good written communication skills.

            ### Scoring:

            | Criteria | Score (1-5) | Comment |
            |---------------------------|-------------|---------|
            | Technical Skills | 5 | Strong experience in all required technologies. |
            | Experience | 5 | Exceeds required years of experience and has leadership experience. |
            | Education | 5 | Holds relevant degree in Computer Science. |
            | Communication Skills | 4 | Well-written CV demonstrates good communication ability. |

            ### Recommendation:
            John Smith is highly suitable for the position with a strong technical background, relevant experience, and appropriate education. His profile indicates he would be a valuable addition to the team.
            """)

    elif process_button or st.session_state.get('analysis_completed'):
        # Process CVs if button was clicked or we already have results
        if not st.session_state['analysis_completed'] and process_button:
            # Process the uploaded CVs
            results = process_cvs(uploaded_files)

            # Store results in session state
            st.session_state['results'] = results
            st.session_state['thread_ids'] = [
                r.get("Thread ID", "") for r in results]
            st.session_state['analysis_completed'] = True

        # Display the results
        display_results(st.session_state.get('results', []))


if __name__ == "__main__":
    main()
