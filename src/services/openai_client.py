"""
Azure OpenAI client for summarizing multiple submission analyses and generating follow-up questions.
"""

import streamlit as st
import requests
import json
from typing import List, Dict, Any, Optional

from config import AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_KEY, AZURE_OPENAI_DEPLOYMENT_NAME


class AzureOpenAIClient:
    """Client for interacting with Azure OpenAI services."""

    def __init__(self, endpoint: str = AZURE_OPENAI_ENDPOINT,
                 api_key: str = AZURE_OPENAI_KEY,
                 deployment_name: str = AZURE_OPENAI_DEPLOYMENT_NAME):
        self.endpoint = endpoint
        self.api_key = api_key
        self.deployment_name = deployment_name

    def get_chat_completion(self,
                            messages: List[Dict[str, str]],
                            temperature: float = 0.7,
                            max_tokens: int = 2000) -> Optional[str]:
        """
        Send a request to Azure OpenAI Chat Completion API.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Controls randomness (0.0 to 1.0)
            max_tokens: Maximum tokens to generate

        Returns:
            Generated content or None if there was an error
        """
        url = f"{self.endpoint}/openai/deployments/{self.deployment_name}/chat/completions?api-version=2023-12-01-preview"

        headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key
        }

        payload = {
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            response_data = response.json()

            if "choices" in response_data and len(response_data["choices"]) > 0:
                return response_data["choices"][0]["message"]["content"]
            else:
                error_msg = "Failed to generate content. The API did not return expected response."
                st.error(error_msg)
                return None
        except Exception as e:
            st.error(f"Azure OpenAI API Error: {str(e)}")
            return None


def extract_analysis_content(analysis: Dict[str, Any]) -> str:
    """
    Extract formatted analysis content from submission analysis data.

    Args:
        analysis: Dictionary containing submission analysis data

    Returns:
        Extracted analysis text
    """
    try:
        analysis_text = ""
        analysis_data = json.loads(analysis.get("Analysis", "{}"))

        for header in analysis_data:
            chat_dict = header.get('__dict__', {})
            chat_name = chat_dict.get('chat_name', '')

            if chat_name in ["summary", "applicant_lookup_agent"]:
                chat_response = chat_dict.get('chat_response', {})
                chat_message = chat_response.get('chat_message', {})
                content = chat_message.get('__dict__', {}).get('content', '')

                if content:
                    analysis_text += content + "\n"

        # If we couldn't extract formatted content, use the raw analysis
        if not analysis_text:
            analysis_text = analysis.get("Analysis", "No analysis available")

    except Exception:
        # Fallback to raw analysis if JSON parsing fails
        analysis_text = analysis.get("Analysis", "No analysis available")

    return analysis_text


def build_comparison_prompt(analyses: List[Dict[str, Any]]) -> str:
    """
    Build a prompt for comparing multiple submission analyses.

    Args:
        analyses: List of submission analysis dictionaries

    Returns:
        Formatted prompt for OpenAI
    """
    prompt = "Please provide a comparative analysis of the following submission analyses:\n\n"

    for analysis in analyses:
        submission_name = analysis.get("Submission Name", "Unnamed Submission")
        analysis_text = extract_analysis_content(analysis)

        prompt += f"Submission: {submission_name}\n"
        prompt += f"Analysis: {analysis_text}\n\n"

    prompt += "Please provide an objective comparative analysis of the submissions based on their qualifications, experience, and skills. Create a table comparing key aspects across all submissions. DO NOT rank the submissions or suggest which one is better than others. The analysis should only highlight differences and similarities in an objective manner."

    return prompt


def build_followup_questions_prompt(analysis: Dict[str, Any]) -> str:
    """
    Build a prompt for generating follow-up questions based on submission analysis.

    Args:
        analysis: Dictionary containing submission analysis data

    Returns:
        Formatted prompt for OpenAI
    """
    submission_name = analysis.get("Submission Name", "Unnamed Submission")
    analysis_text = extract_analysis_content(analysis)

    prompt = f"""Generate 5 tailored follow-up questions for the submission based on the following analysis:

Submission: {submission_name}
Analysis: {analysis_text}

Please include:
1. Questions that clarify points that need more explanation or context
2. Questions about specific experiences or skills mentioned that would benefit from elaboration 
3. Questions about areas where the submission might have relevant content not mentioned 
4. Questions that help understand the intentions, goals, and motivations behind the submission
5. Questions about preferences or additional details that would enhance understanding of the submission

Format the questions as a numbered list with brief explanations for why each question is important to ask.
"""

    return prompt


def generate_followup_questions(analysis: Dict[str, Any]) -> str:
    """
    Generate tailored follow-up questions based on a submission analysis.

    Args:
        analysis: Dictionary containing submission analysis data

    Returns:
        List of follow-up questions with explanations
    """
    client = AzureOpenAIClient()
    prompt = build_followup_questions_prompt(analysis)

    system_message = {
        "role": "system",
        "content": "You are an AI assistant for the SoCa (Submission over Criteria) tool that helps prepare follow-up questions for submissions. Your questions should help gather additional information, clarify details, and better understand the submission's content. Be specific, professional, and conversational."
    }

    user_message = {
        "role": "user",
        "content": prompt
    }

    result = client.get_chat_completion(
        messages=[system_message, user_message],
        temperature=0.7,
        max_tokens=1500
    )

    return result if result else "Failed to generate follow-up questions due to an error."


def summarize_submission_analyses(analyses: List[Dict[str, Any]]) -> str:
    """
    Summarize multiple submission analyses using Azure OpenAI.

    Args:
        analyses: List of submission analysis dictionaries

    Returns:
        Comprehensive comparison of the submission analyses
    """
    client = AzureOpenAIClient()
    prompt = build_comparison_prompt(analyses)

    system_message = {
        "role": "system",
        "content": "You are an AI assistant for the SoCa (Submission over Criteria) tool that helps compare and summarize multiple submission analyses. Provide objective, factual comparisons without ranking submissions or indicating which ones are better. Focus on highlighting differences in qualifications, skills, and experience without making value judgments."
    }

    user_message = {
        "role": "user",
        "content": prompt
    }

    result = client.get_chat_completion(
        messages=[system_message, user_message],
        temperature=0.7,
        max_tokens=2000
    )

    return result if result else "Failed to generate comparative analysis due to an error."
