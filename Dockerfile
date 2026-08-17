# Use Python 3.12 official image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV SECRET_KEY=dummy-secret-key-for-build

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project
COPY . .

# Create dummy .env file for build
RUN echo "SECRET_KEY=dummy-secret-key-for-build" > .env

# Collect static files (using dummy SECRET_KEY for build)
RUN python manage.py collectstatic --no-input

# Expose port (Render uses 10000 by default)
EXPOSE 10000

# Start the server
CMD ["gunicorn", "config.wsgi", "--log-file", "-", "--bind", "0.0.0.0:10000"]