FROM tiangolo/uwsgi-nginx-flask:python3.9

ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production
ENV FLASK_APP=/app/run.py
ENV UWSGI_MODULE=run         
ENV UWSGI_CALLABLE=app       

WORKDIR /app

COPY requirements.txt /tmp/
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r /tmp/requirements.txt \
    && pip install psycopg2-binary

COPY ./app /app/app
COPY run.py /app/run.py
COPY uwsgi.ini /app/uwsgi.ini

COPY .env /app/.env
