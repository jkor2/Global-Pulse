FROM python:3.11-slim

# Set the working directory
WORKDIR /code

# Install system dependencies (same as API if needed)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project
COPY . .

# Ensures the app package can be imported
ENV PYTHONPATH="/code"

# Default command for test container
CMD ["pytest", "-q"]