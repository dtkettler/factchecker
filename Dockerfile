FROM python:3.9-slim

ENV PYTHONUNBUFFERED True

ENV APP_HOME /app

ENV PORT 8080

WORKDIR $APP_HOME

COPY . ./

RUN pip install --no-cache-dir -r requirements.txt

RUN python sqlite_setup.py

RUN python query.py "Dr. Fauci does not exist"

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app