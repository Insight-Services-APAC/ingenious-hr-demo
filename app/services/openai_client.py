"""
Azure OpenAI client for summarizing multiple CV analyses.
"""

import streamlit as st
import requests
import json
from typing import List, Dict, Any

from config import AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_KEY, AZURE_OPENAI_DEPLOYMENT_NAME


def summarize_cv_analyses(analyses: List[Dict[str, Any]]) -> str:
    """Summarize multiple CV analyses using Azure OpenAI."""
    url = f"{AZURE_OPENAI_ENDPOINT}/openai/deployments/{AZURE_OPENAI_DEPLOYMENT_NAME}/chat/completions?api-version=2023-12-01-preview"

    # Prepare the prompt with all CV summaries
    prompt = "Please provide a comprehensive comparison and summary of the following CV analyses:\n\n"

    for analysis in analyses:
        cv_name = analysis.get("CV Name", "Unnamed CV")

        # Try to extract formatted analysis content if possible
        try:
            analysis_text = ""
            analysis_data = json.loads(analysis.get("Analysis", "{}"))

            for header in analysis_data:
                chat_dict = header.get('__dict__', {})
                chat_name = chat_dict.get('chat_name', '')

                if chat_name in ["summary", "applicant_lookup_agent"]:
                    chat_response = chat_dict.get('chat_response', {})
                    chat_message = chat_response.get('chat_message', {})
                    content = chat_message.get(
                        '__dict__', {}).get('content', '')

                    if content:
                        analysis_text += content + "\n"

            # If we couldn't extract formatted content, use the raw analysis
            if not analysis_text:
                analysis_text = analysis.get(
                    "Analysis", "No analysis available")

        except Exception:
            # Fallback to raw analysis if JSON parsing fails
            analysis_text = analysis.get("Analysis", "No analysis available")

        prompt += f"CV: {cv_name}\n"
        prompt += f"Analysis: {analysis_text}\n\n"

    prompt += "Please compare the candidates based on their qualifications, experience, skills, and overall suitability for the position. Highlight the strongest candidates and explain why. Create a table comparing key aspects across all candidates and provide a final ranking with rationale."

    # Prepare the API request
    headers = {
        "Content-Type": "application/json",
        "api-key": AZURE_OPENAI_KEY
    }

    payload = {
        "messages": [
            {"role": "system", "content": "You are an AI assistant that helps compare and summarize multiple CV analyses for recruitment purposes. Provide detailed comparisons and clear recommendations."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 2000
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        response_data = response.json()

        # Extract the summary from the response
        if "choices" in response_data and len(response_data["choices"]) > 0:
            return response_data["choices"][0]["message"]["content"]
        else:
            return "Failed to generate summary. The API did not return expected content."
    except Exception as e:
        st.error(f"Azure OpenAI API Error: {str(e)}")
        return f"Error generating summary: {str(e)}"
