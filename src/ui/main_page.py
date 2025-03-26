"""
Main page UI logic for the SoCa (Submission over Criteria) Analysis Tool.
"""

import streamlit as st
import json
import time
import pandas as pd
import pyperclip
from typing import List, Dict, Any

from services import APIClient, extract_text_from_file, summarize_submission_analyses
from services.openai_client import generate_followup_questions
from ui.components import display_feedback_buttons, create_download_link


def process_submissions(uploaded_files) -> List[Dict[str, Any]]:
    """Process uploaded submission files and send them to the API for analysis."""
    results = []

    with st.spinner("Analyzing Submissions..."):
        progress_bar = st.progress(0)

        for i, uploaded_file in enumerate(uploaded_files):
            # Update progress
            progress = (i + 1) / len(uploaded_files)
            progress_bar.progress(progress)

            # Extract text
            submission_text = extract_text_from_file(uploaded_file)

            # Send to API
            identifier = f"submission_{i+1}"
            response = APIClient.create_chat(
                submission_text, identifier=identifier)

            # Log the response for debugging if needed
            if "error" in response:
                st.error(
                    f"Error analyzing {uploaded_file.name}: {response['error']}")
                continue

            # Store result
            result = {
                "Submission Name": uploaded_file.name,
                "Analysis": response.get("agent_response", "Analysis failed"),
                "Thread ID": response.get("thread_id", ""),
                "Message ID": response.get("message_id", "")
            }
            results.append(result)

        # Reset summary state when processing new submissions
        if 'summary_generated' in st.session_state:
            st.session_state['summary_generated'] = False
            if 'summary_content' in st.session_state:
                del st.session_state['summary_content']

    return results


def display_results(results: List[Dict[str, Any]]):
    """Display the analysis results for the uploaded submissions."""
    if not results:
        return

    st.header("SoCa Analysis Results")
    st.markdown("*Submission over Criteria assessment*")

    # Create tabs for each submission, a summary tab, and a follow-up questions tab
    tab_names = [result["Submission Name"] for result in results] + \
        ["🔍 Comparative Analysis", "🔗 Follow-up Questions"]
    tabs = st.tabs(tab_names)

    # Display individual submission tabs
    # All tabs except the last two (comparative analysis and follow-up questions)
    for i, tab in enumerate(tabs[:-2]):
        with tab:
            result = results[i]

            # Submission name and metadata
            st.subheader(f"Submission: {result['Submission Name']}")

            # Analysis result
            st.markdown("### Analysis")

            # Parse and display the analysis
            try:
                analysis_data = json.loads(result["Analysis"])
                for header in analysis_data:
                    chat_dict = header.get('__dict__', {})
                    chat_name = chat_dict.get('chat_name', '')

                    if chat_name in ["summary"]:
                        chat_response = chat_dict.get('chat_response', {})
                        chat_message = chat_response.get('chat_message', {})
                        content = chat_message.get(
                            '__dict__', {}).get('content', '')

                        if content:
                            st.markdown(content)
            except Exception as e:
                st.error(f"Error displaying analysis: {str(e)}")
                st.markdown(result["Analysis"])

            # Display feedback buttons
            display_feedback_buttons(result, i)

    # Check if we need to automatically generate a new summary
    if not st.session_state.get('summary_generated', False) or 'summary_content' not in st.session_state:
        # Generate the summary automatically when results are first displayed
        try:
            with st.spinner("Generating comparative analysis of all submissions..."):
                # Check if OpenAI API credentials are configured
                from config import AZURE_OPENAI_KEY, AZURE_OPENAI_ENDPOINT
                if not AZURE_OPENAI_KEY or not AZURE_OPENAI_ENDPOINT:
                    st.session_state['summary_generated'] = False
                    st.session_state['summary_content'] = "⚠️ Azure OpenAI API credentials not configured. Please add them to your .env file to enable the comparative analysis feature."
                else:
                    # Generate summary using Azure OpenAI
                    summary = summarize_submission_analyses(results)

                    # Store in session state
                    st.session_state['summary_generated'] = True
                    st.session_state['summary_content'] = summary
        except Exception as e:
            st.session_state['summary_generated'] = False
            st.session_state[
                'summary_content'] = f"⚠️ Error generating analysis: {str(e)}. Please check your Azure OpenAI API credentials."

    # Display summary tab
    with tabs[-2]:
        st.subheader("Objective Comparative Analysis")
        st.markdown("*Comparing submissions against the defined criteria*")

        # Display the summary (either newly generated or from cache)
        st.markdown(st.session_state.get('summary_content', ''))

        # Provide button to regenerate if needed
        if st.button("Regenerate Analysis", key="regenerate_summary"):
            with st.spinner("Regenerating comparative analysis..."):
                try:
                    # Check if OpenAI API credentials are configured
                    from config import AZURE_OPENAI_KEY, AZURE_OPENAI_ENDPOINT
                    if not AZURE_OPENAI_KEY or not AZURE_OPENAI_ENDPOINT:
                        st.error(
                            "Azure OpenAI API credentials not configured. Please add them to your .env file.")
                    else:
                        # Generate fresh summary using Azure OpenAI
                        summary = summarize_submission_analyses(results)

                        # Update session state
                        st.session_state['summary_generated'] = True
                        st.session_state['summary_content'] = summary

                        # Refresh the UI
                        st.rerun()
                except Exception as e:
                    st.error(f"Error generating analysis: {str(e)}")

    # Display follow-up questions tab
    with tabs[-1]:
        st.subheader("Generate Follow-up Questions")
        st.markdown("*Create targeted questions based on submission analysis*")

        st.markdown("""
        Generate tailored follow-up questions based on a submission's analysis. 
        These questions will help clarify information, explore potential areas of interest, 
        and gather additional insights about the submission.
        """)

        # Initialize session state for follow-up questions if not exists
        if 'followup_questions' not in st.session_state:
            st.session_state['followup_questions'] = {}

        # Dropdown to select a submission
        submission_options = [result["Submission Name"] for result in results]
        selected_submission = st.selectbox(
            "Select a Submission", submission_options, key="followup_submission_selector")

        # Get the selected submission's index
        selected_index = submission_options.index(selected_submission)
        selected_result = results[selected_index]

        # Generate follow-up questions button
        generate_button = st.button(
            "Generate Follow-up Questions", type="primary", key="generate_questions")

        # Check if we should display existing questions or generate new ones
        if generate_button:
            try:
                # Check if OpenAI API credentials are configured
                from config import AZURE_OPENAI_KEY, AZURE_OPENAI_ENDPOINT
                if not AZURE_OPENAI_KEY or not AZURE_OPENAI_ENDPOINT:
                    st.error(
                        "Azure OpenAI API credentials not configured. Please add them to your .env file.")
                else:
                    # Generate follow-up questions using Azure OpenAI
                    with st.spinner(f"Generating tailored follow-up questions for {selected_submission}..."):
                        questions = generate_followup_questions(
                            selected_result)

                        # Store in session state with submission name as key
                        st.session_state['followup_questions'][selected_submission] = questions

                        # Display the questions
                        st.markdown("### Tailored Follow-up Questions")
                        st.markdown(questions)

                        # Add copy to clipboard functionality
                        if st.button("📋 Copy Questions to Clipboard", key="copy_questions"):
                            try:
                                pyperclip.copy(questions)
                                st.success("Questions copied to clipboard!")
                            except Exception:
                                st.error(
                                    "Unable to copy to clipboard. Please select and copy manually.")

                        # Add export functionality
                        export_questions = create_download_link(
                            questions,
                            f"followup_questions_{selected_submission.replace(' ', '_')}.txt",
                            "📥 Download Questions as Text File"
                        )
                        st.markdown(export_questions, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error generating follow-up questions: {str(e)}")
        elif selected_submission in st.session_state['followup_questions']:
            # Display existing questions from session state
            st.markdown("### Tailored Follow-up Questions")
            st.markdown(
                st.session_state['followup_questions'][selected_submission])

            # Add copy to clipboard functionality
            if st.button("📋 Copy Questions to Clipboard", key="copy_existing_questions"):
                try:
                    pyperclip.copy(
                        st.session_state['followup_questions'][selected_submission])
                    st.success("Questions copied to clipboard!")
                except Exception:
                    st.error(
                        "Unable to copy to clipboard. Please select and copy manually.")

            # Add export functionality
            export_questions = create_download_link(
                st.session_state['followup_questions'][selected_submission],
                f"followup_questions_{selected_submission.replace(' ', '_')}.txt",
                "📥 Download Questions as Text File"
            )
            st.markdown(export_questions, unsafe_allow_html=True)

            # Add regenerate button
            if st.button("🔄 Regenerate Questions", key="regenerate_questions"):
                # Remove existing questions to force regeneration
                if selected_submission in st.session_state['followup_questions']:
                    del st.session_state['followup_questions'][selected_submission]
                st.rerun()
        else:
            st.info(
                "Click the 'Generate Follow-up Questions' button to create tailored questions for this submission.")
