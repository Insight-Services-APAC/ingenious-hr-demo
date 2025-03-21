# Dockerfile for Streamlit App with Azure Storage Support

FROM python:3.10

RUN pip install --upgrade pip

# Set environment variable to ensure streamlit runs correctly in Docker
ENV STREAMLIT_SERVER_PORT=8080
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

EXPOSE 8080

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt 


ENTRYPOINT ["streamlit", "run", "streamlit_app.py"]
#CMD streamlit run app.py