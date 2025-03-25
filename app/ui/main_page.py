"""
Main page UI logic for the CV Analysis Tool.
"""

import streamlit as st
import json
import time
import pandas as pd
from typing import List, Dict, Any

from services import APIClient, extract_text_from_file, summarize_cv_analyses
from ui.components import display_feedback_buttons


def process_cvs(uploaded_files) -> List[Dict[str, Any]]:
    """Process uploaded CV files and send them to the API for analysis."""
    results = []

    with st.spinner("Analyzing CVs..."):
        progress_bar = st.progress(0)

        for i, uploaded_file in enumerate(uploaded_files):
            # Update progress
            progress = (i + 1) / len(uploaded_files)
            progress_bar.progress(progress)

            # Extract text
            cv_text = extract_text_from_file(uploaded_file)

            # Send to API
            identifier = f"cv_{i+1}"
            response = APIClient.create_chat(
                cv_text, identifier=identifier)

            # Log the response for debugging if needed
            if "error" in response:
                st.error(
                    f"Error analyzing {uploaded_file.name}: {response['error']}")
                continue

            # Store result
            result = {
                "CV Name": uploaded_file.name,
                "Analysis": response.get("agent_response", "Analysis failed"),
                "Thread ID": response.get("thread_id", ""),
                "Message ID": response.get("message_id", "")
            }
            results.append(result)

            # Simulate API delay to not overwhelm the server
            time.sleep(0.5)

        # Reset summary state when processing new CVs
        if 'summary_generated' in st.session_state:
            st.session_state['summary_generated'] = False
            if 'summary_content' in st.session_state:
                del st.session_state['summary_content']

    return results


def display_results(results: List[Dict[str, Any]]):
    """Display the analysis results for the uploaded CVs."""
    if not results:
        return

    st.header("Analysis Results")

    # Create tabs for each CV and a summary tab
    tab_names = [result["CV Name"]
                 for result in results] + ["🔍 Comparative Summary"]
    tabs = st.tabs(tab_names)

    # Display individual CV tabs
    # All tabs except the last one (summary)
    for i, tab in enumerate(tabs[:-1]):
        with tab:
            result = results[i]

            # CV name and metadata
            st.subheader(f"CV: {result['CV Name']}")

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
            with st.spinner("Generating comparative summary of all CVs..."):
                # Check if OpenAI API credentials are configured
                from config import AZURE_OPENAI_KEY, AZURE_OPENAI_ENDPOINT
                if not AZURE_OPENAI_KEY or not AZURE_OPENAI_ENDPOINT:
                    st.session_state['summary_generated'] = False
                    st.session_state['summary_content'] = "⚠️ Azure OpenAI API credentials not configured. Please add them to your .env file to enable the comparative summary feature."
                else:
                    # Generate summary using Azure OpenAI
                    summary = summarize_cv_analyses(results)

                    # Store in session state
                    st.session_state['summary_generated'] = True
                    st.session_state['summary_content'] = summary
        except Exception as e:
            st.session_state['summary_generated'] = False
            st.session_state[
                'summary_content'] = f"⚠️ Error generating summary: {str(e)}. Please check your Azure OpenAI API credentials."

    # Display summary tab
    with tabs[-1]:
        st.subheader("Comparative Summary of All CVs")

        # Display the summary (either newly generated or from cache)
        st.markdown(st.session_state.get('summary_content', ''))

        # Provide button to regenerate if needed
        if st.button("Regenerate Summary", key="regenerate_summary"):
            with st.spinner("Regenerating comprehensive comparison..."):
                try:
                    # Check if OpenAI API credentials are configured
                    from config import AZURE_OPENAI_KEY, AZURE_OPENAI_ENDPOINT
                    if not AZURE_OPENAI_KEY or not AZURE_OPENAI_ENDPOINT:
                        st.error(
                            "Azure OpenAI API credentials not configured. Please add them to your .env file.")
                    else:
                        # Generate fresh summary using Azure OpenAI
                        summary = summarize_cv_analyses(results)

                        # Update session state
                        st.session_state['summary_generated'] = True
                        st.session_state['summary_content'] = summary

                        # Refresh the UI
                        st.rerun()
                except Exception as e:
                    st.error(f"Error generating summary: {str(e)}")
