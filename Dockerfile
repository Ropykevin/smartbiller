# Use the tiangolo/uwsgi-nginx-flask image with Python 3.9
FROM tiangolo/uwsgi-nginx-flask:python3.9

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=run.py
ENV FLASK_ENV=production

# Install dependencies
COPY requirements.txt /tmp/
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r /tmp/requirements.txt \
    && pip install psycopg2-binary

# Copy the Flask app
COPY ./app /app/app  # app code goes in /app/app
COPY run.py /app/run.py  # make sure this exists
COPY .env /app/.env
