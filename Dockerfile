# Dockerfile untuk Railway deployment
FROM python:3.11.7-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y     gcc     pkg-config     libpq-dev     curl     && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Expose port (Railway akan set PORT secara otomatis)
EXPOSE 8000

# Health check - gunakan port 8000 sebagai default atau PORT dari env
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3     CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Start command menggunakan run.py yang sudah menangani PORT dengan benar
CMD ["python", "run.py"]
