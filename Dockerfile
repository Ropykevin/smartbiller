# Use the tiangolo/uwsgi-nginx-flask image with Python 3.9
FROM tiangolo/uwsgi-nginx-flask:python3.9

# Set environment variables to prevent Python from buffering outputs
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=run.py
ENV FLASK_ENV=production

# Copy requirements.txt first for better caching
COPY requirements.txt /tmp/

# Upgrade pip and install Python packages
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r /tmp/requirements.txt \
    && pip install psycopg2-binary

# Copy the entire application
COPY . /app/

# Create necessary directories
RUN mkdir -p /app/logs /app/instance

# Set proper permissions
RUN chmod +x /app/run_scheduled_tasks.py

# Create a non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port 80 (handled by nginx in the base image)
EXPOSE 80