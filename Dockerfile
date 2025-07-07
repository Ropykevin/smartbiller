FROM tiangolo/uwsgi-nginx-flask:python3.9

ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production
ENV FLASK_APP=/app/run.py
ENV UWSGI_MODULE=run         # ✅ this tells uWSGI to use run.py
ENV UWSGI_CALLABLE=app       # ✅ this tells uWSGI to look for 'app = Flask(__name__)'

WORKDIR /app

COPY requirements.txt /tmp/
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r /tmp/requirements.txt \
    && pip install psycopg2-binary

COPY ./app /app/app
COPY run.py /app/run.py
COPY .env /app/.env
