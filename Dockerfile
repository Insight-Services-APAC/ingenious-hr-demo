# Dockerfile for Streamlit App with Azure Storage Support
# syntax=docker/dockerfile:1
FROM docker.io/library/python:3.12-slim

# Set environment variable to ensure streamlit runs correctly in Docker
ENV STREAMLIT_SERVER_PORT=8080
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

EXPOSE 8080

WORKDIR /usr/src/app

COPY ./src .
COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["streamlit", "run", "app.py"]
