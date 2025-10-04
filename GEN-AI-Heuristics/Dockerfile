# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set maintainer and version labels
LABEL maintainer="Heuristic Evaluation Team" \
      version="1.0.0" \
      description="Heuristic Evaluation Streamlit App with Playwright"

# Set working directory
WORKDIR /app

# Update system packages and install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    gnupg \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright (Python package)
RUN pip install playwright

# Copy application files
COPY main.py .
COPY html_generator.py .

# Copy .env file if it exists (make it optional)
COPY .env* ./

# Prepare shared browsers path and install browsers as root
RUN mkdir -p /ms-playwright
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
ENV XDG_CACHE_HOME=/ms-playwright
RUN playwright install --with-deps

# Create a non-root user for security and fix permissions
RUN groupadd -g 1002 appgroup && \
    useradd -u 1002 -g appgroup -m appuser && \
    chown -R appuser:appgroup /app /ms-playwright

# Expose Streamlit's default port
EXPOSE 8501

# Switch to non-root user
USER appuser

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