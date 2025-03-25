"""
Azure OpenAI client for summarizing multiple CV analyses.
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
    Extract formatted analysis content from CV analysis data.
    
    Args:
        analysis: Dictionary containing CV analysis data
        
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
    Build a prompt for comparing multiple CV analyses.
    
    Args:
        analyses: List of CV analysis dictionaries
        
    Returns:
        Formatted prompt for OpenAI
    """
    prompt = "Please provide a comprehensive comparison and summary of the following CV analyses:\n\n"
    
    for analysis in analyses:
        cv_name = analysis.get("CV Name", "Unnamed CV")
        analysis_text = extract_analysis_content(analysis)
        
        prompt += f"CV: {cv_name}\n"
        prompt += f"Analysis: {analysis_text}\n\n"
    
    prompt += "Please compare the candidates based on their qualifications, experience, skills, and overall suitability for the position. Highlight the strongest candidates and explain why. Create a table comparing key aspects across all candidates and provide a final ranking with rationale."
    
    return prompt


def summarize_cv_analyses(analyses: List[Dict[str, Any]]) -> str:
    """
    Summarize multiple CV analyses using Azure OpenAI.
    
    Args:
        analyses: List of CV analysis dictionaries
        
    Returns:
        Comprehensive summary and comparison of the CV analyses
    """
    client = AzureOpenAIClient()
    prompt = build_comparison_prompt(analyses)
    
    system_message = {
        "role": "system", 
        "content": "You are an AI assistant that helps compare and summarize multiple CV analyses for recruitment purposes. Provide detailed comparisons and clear recommendations."
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
    
    return result if result else "Failed to generate summary due to an error."