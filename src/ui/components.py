"""
UI components and utilities for the CV Analysis Tool.
"""

import base64
import streamlit as st
from typing import Dict, Any


def create_download_link(content, filename, text):
    """Create a download link for exporting results."""
    b64 = base64.b64encode(content.encode()).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="{filename}">{text}</a>'
    return href


def process_api_response(response_data: Dict[str, Any]) -> str:
    """Process and format the API response for display."""
    try:
        # For the current implementation, we'll just extract the response content
        # This can be expanded to include more sophisticated formatting
        if "agent_response" in response_data:
            return response_data["agent_response"]
        return "Analysis failed to retrieve a response"
    except Exception as e:
        st.error(f"Error processing API response: {str(e)}")
        return f"Error processing analysis: {str(e)}"


def display_feedback_buttons(result, index):
    """Display feedback buttons for analysis results."""
    from services import APIClient

    col1, col2 = st.columns(2)
    with col1:
        if st.button("👍 Helpful", key=f"helpful_{index}"):
            feedback = APIClient.submit_feedback(
                result["Message ID"],
                result["Thread ID"],
                True
            )
            st.success("Thank you for your feedback!")

    with col2:
        if st.button("👎 Not Helpful", key=f"not_helpful_{index}"):
            feedback = APIClient.submit_feedback(
                result["Message ID"],
                result["Thread ID"],
                False
            )
            st.success(
                "Thank you for your feedback. We'll improve our analysis.")
