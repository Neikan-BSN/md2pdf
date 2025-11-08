# Multi-stage build for md2pdf
FROM python:3.11-slim as python-base

# Install Node.js 18.x
RUN apt-get update && \
    apt-get install -y curl gnupg && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy Python requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Node.js package files and install
COPY renderer/package.json renderer/
RUN cd renderer && npm install --production

# Copy application files
COPY md2pdf.py .
COPY markdown_renderer.py .
COPY theme_manager.py .
COPY config_loader.py .
COPY renderer_client.py .
COPY md2pdf.config.yaml .
COPY themes/ themes/
COPY templates/ templates/
COPY renderer/server.js renderer/

# Set Docker environment variable (for sandbox disabling)
ENV DOCKER=true

# Create directory for conversions
RUN mkdir -p /data/converted

# Set working directory to /data for user files
WORKDIR /data

# Entry point
ENTRYPOINT ["python3", "/app/md2pdf.py"]
