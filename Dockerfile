FROM python:3.8 as backend
WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app .
COPY ./app/docker-entrypoint.sh /docker-entrypoint.sh