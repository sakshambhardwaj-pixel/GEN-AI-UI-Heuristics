# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set maintainer and version labels
LABEL maintainer="Heuristic Evaluation Team" \
      version="1.0.0" \
      description="Heuristic Evaluation Streamlit App with Playwright"

# Set working directory
WORKDIR /app

# Install system dependencies required by Playwright
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright (if not in requirements.txt)
RUN pip install playwright

# Set Playwright browsers path
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
ENV XDG_CACHE_HOME=/ms-playwright

# Create browsers directory and install browsers as root
RUN mkdir -p /ms-playwright && \
    playwright install --with-deps chromium

# Create a non-root user for security
RUN groupadd -g 1002 appgroup && \
    useradd -u 1002 -g appgroup -m appuser

# Copy application files and set ownership
COPY --chown=appuser:appgroup main.py .
COPY --chown=appuser:appgroup html_generator.py .

# Copy .env file if it exists (make it optional)
# Use a shell form to avoid Docker COPY error when file does not exist
RUN if [ -f .env ]; then cp .env /app/.env; fi && \
    if ls .env.* 1> /dev/null 2>&1; then cp .env.* /app/; fi && \
    chown appuser:appgroup /app/.env* 2>/dev/null || true

# Fix permissions for browser directory and app directory
RUN chown -R appuser:appgroup /app /ms-playwright && \
    chmod -R 755 /ms-playwright

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
