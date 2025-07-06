# Use tiangolo image with Python 3.9
FROM tiangolo/uwsgi-nginx-flask:python3.9

# Environment configuration
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production
ENV FLASK_APP=/app/run.py  # MUST be full path

# Install dependencies
COPY requirements.txt /tmp/
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r /tmp/requirements.txt && \
    pip install psycopg2-binary

# Copy application code
COPY ./app /app/app
COPY run.py /app/run.py
COPY .env /app/.env

# Optional: expose port (already handled by tiangolo image)
EXPOSE 80
