FROM tiangolo/uwsgi-nginx-flask:python3.9

# Prevent Python from buffering output
ENV PYTHONUNBUFFERED=1

# Set Flask app path
ENV FLASK_ENV=production
ENV FLASK_APP=/app/run.py

# Install dependencies
COPY requirements.txt /tmp/
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r /tmp/requirements.txt \
    && pip install psycopg2-binary

# Copy app files
COPY ./app /app/app
COPY run.py /app/run.py
COPY .env /app/.env
