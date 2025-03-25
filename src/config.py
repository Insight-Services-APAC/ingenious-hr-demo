"""
Configuration settings for the CV Analysis Tool.
Loads environment variables and provides application configuration.
"""

import os
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
API_BASE_URL = os.getenv(
    "API_BASE_URL", "https://hr-demo-app.ambitiousriver-e696f55c.australiaeast.azurecontainerapps.io/api/v1")
API_USERNAME = os.getenv("API_USERNAME", "")
API_PASSWORD = os.getenv("API_PASSWORD", "")
DEFAULT_REVISION_ID = os.getenv(
    "REVISION_ID", "5ccc4a42-1e24-4b82-a550-e7e9c6ffa48b")

# Azure Blob Storage Configuration
AZURE_BLOB_STORAGE_URL = os.getenv("AZURE_BLOB_STORAGE_URL", "")

# Azure OpenAI API Configuration
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY", "")
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv(
    "AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o-mini")

# Streamlit page configuration


def configure_page():
    """Configure the Streamlit page settings."""
    st.set_page_config(
        page_title="CV Analysis Tool",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="expanded"
    )
