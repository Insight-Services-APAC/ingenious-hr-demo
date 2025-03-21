"""
Azure Blob Storage client for uploading and downloading files.
"""

import streamlit as st
from typing import Optional
from urllib.parse import urlparse
from azure.storage.blob import BlobServiceClient, ContentSettings

from config import AZURE_BLOB_STORAGE_URL
import os


class AzureBlobClient:
    """Client for interacting with Azure Blob Storage using a full URL with SAS token."""

    def __init__(self):
        # Get the full URL from environment variable
        self.full_url = os.getenv("AZURE_BLOB_STORAGE_URL", "")

        # Check if URL is provided
        if not self.full_url:
            raise ValueError(
                "AZURE_BLOB_STORAGE_URL environment variable is not set or is empty")

        # Parse the URL to extract components
        try:
            from urllib.parse import urlparse, parse_qs

            parsed_url = urlparse(self.full_url)
            st.debug(f"Parsed URL: {parsed_url}")

            # The path starts with a /, so split and filter empty strings
            path_parts = [part for part in parsed_url.path.split('/') if part]
            st.debug(f"Path parts: {path_parts}")

            if len(path_parts) < 1:
                raise ValueError("URL does not contain container information")

            self.container_name = path_parts[0]
            st.debug(f"Container name: {self.container_name}")

            # Extract the base URL without path and query
            self.account_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            st.debug(f"Account URL: {self.account_url}")

            # Get the SAS token from the query string
            self.sas_token = parsed_url.query
            st.debug(f"SAS token length: {len(self.sas_token)}")

            # Check if SAS token appears to be valid
            if not self.sas_token.startswith('sv=') and not self.sas_token.startswith('?sv='):
                st.warning(
                    "SAS token doesn't appear to be in the expected format")

            # Create a direct connection to the blob service
            try:
                # Alternative 1: Use BlobServiceClient
                self.blob_service_client = BlobServiceClient(
                    f"{self.account_url}?{self.sas_token}"
                )
                st.success(
                    "Successfully created BlobServiceClient using direct URL")
            except Exception as e1:
                st.error(
                    f"Failed to create BlobServiceClient using direct URL: {str(e1)}")
                st.info("Trying alternative connection method...")

                try:
                    # Alternative 2: Use from_connection_string
                    self.blob_service_client = BlobServiceClient.from_connection_string(
                        f"BlobEndpoint={self.account_url};SharedAccessSignature={self.sas_token}"
                    )
                    st.success(
                        "Successfully created BlobServiceClient using connection string")
                except Exception as e2:
                    st.error(
                        f"Failed to create BlobServiceClient using connection string: {str(e2)}")

                    # Alternative 3: Try another format
                    try:
                        # Remove any leading ? from SAS token if present
                        clean_sas = self.sas_token[1:] if self.sas_token.startswith(
                            '?') else self.sas_token
                        self.blob_service_client = BlobServiceClient(
                            f"{self.account_url}?{clean_sas}"
                        )
                        st.success(
                            "Successfully created BlobServiceClient using cleaned SAS token")
                    except Exception as e3:
                        raise ValueError(
                            f"All connection attempts failed: {str(e3)}")

        except Exception as e:
            raise ValueError(f"Failed to parse Blob Storage URL: {str(e)}")

    def upload_blob(self, content: str, blob_name: str, content_type: str = "application/json") -> bool:
        """Upload content to Azure Blob Storage."""
        try:
            st.info(
                f"Attempting to upload blob: {blob_name} to container: {self.container_name}")

            # Get a client to interact with the specified blob
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            st.info(
                f"Created blob client for: {blob_client.url.split('?')[0]}")

            # Set the content type
            content_settings = ContentSettings(content_type=content_type)

            # Upload the content
            st.info("Starting upload...")
            upload_result = blob_client.upload_blob(
                content,
                overwrite=True,
                content_settings=content_settings
            )
            st.success(f"Upload completed successfully: {upload_result}")
            return True
        except Exception as e:
            st.error(f"Azure Blob Error during upload: {str(e)}")
            import traceback
            st.error(f"Traceback: {traceback.format_exc()}")
            return False

    def download_blob(self, blob_name: str) -> Optional[str]:
        """Download content from Azure Blob Storage."""
        try:
            st.info(
                f"Attempting to download blob: {blob_name} from container: {self.container_name}")

            # Get a client to interact with the specified blob
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            st.info(
                f"Created blob client for: {blob_client.url.split('?')[0]}")

            # Download the blob content
            st.info("Starting download...")
            download_stream = blob_client.download_blob()
            content = download_stream.readall().decode('utf-8')
            st.success("Download completed successfully")

            return content
        except Exception as e:
            st.error(f"Azure Blob Error during download: {str(e)}")
            import traceback
            st.error(f"Traceback: {traceback.format_exc()}")
            return None
