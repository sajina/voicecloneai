# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies (required for mysqlclient)
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# We do NOT run collectstatic here because it requires DB access/Secret Key.
# The entrypoint.sh handles it at runtime.

# Expose port
EXPOSE 8000

# Command to run the application
# Copy startup script
COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

CMD ["/app/entrypoint.sh"]
