# Use smaller Python slim image
FROM python:3.11-slim

LABEL maintainer="Heuristic Evaluation Team" \
      version="1.0.0" \
      description="Heuristic Evaluation Streamlit App"

WORKDIR /app

# Install system dependencies (minimal set)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright and only Chromium (smallest browser)
RUN pip install playwright && \
    playwright install chromium && \
    playwright install-deps chromium

# Copy application files
COPY main.py .
COPY html_generator.py .
# Copy .env file(s) if present (ignore if not found)
RUN if ls .env* 1> /dev/null 2>&1; then cp .env* .; fi

EXPOSE 8501

# Streamlit environment variables
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

ENTRYPOINT ["streamlit", "run"]
CMD ["main.py", "--server.port=8501", "--server.address=0.0.0.0"]
