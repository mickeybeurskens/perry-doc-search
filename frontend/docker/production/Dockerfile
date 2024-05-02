# app/Dockerfile

FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install poetry
RUN poetry config virtualenvs.create false
COPY pyproject.toml ./
COPY README.md ./
COPY perry ./perry
RUN poetry install 

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "🕵_Chat.py", "--server.port=8501", "--server.address=0.0.0.0", "--client.toolbarMode=minimal", "--browser.gatherUsageStats=false"]
