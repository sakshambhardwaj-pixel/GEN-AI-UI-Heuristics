# Use official Playwright Python image (already includes browsers and dependencies)
FROM mcr.microsoft.com/playwright/python:v1.48.0-noble

# Set maintainer and version labels
LABEL maintainer="Heuristic Evaluation Team" \
      version="1.0.0" \
      description="Heuristic Evaluation Streamlit App with Playwright"

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY main.py .
COPY html_generator.py .

# Copy .env file if it exists (make it optional)
RUN if [ -f .env ]; then cp .env /app/; fi

# Expose Streamlit's default port
EXPOSE 8501

# Set environment variables for Streamlit
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Run the Streamlit app
ENTRYPOINT ["streamlit", "run"]
CMD ["main.py", "--server.port=8501", "--server.address=0.0.0.0"]