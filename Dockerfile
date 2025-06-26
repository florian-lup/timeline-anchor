FROM python:3.11-slim

# Install system dependencies (optional build tools for python packages)
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy app files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port for Runway.com
ENV PORT=8080
EXPOSE $PORT

# Default command
CMD ["sh", "-c", "uvicorn api:app --host 0.0.0.0 --port ${PORT:-8080}"] 