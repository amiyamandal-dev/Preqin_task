FROM python:3.9-slim-buster

RUN pip install "uvicorn[standard]" gunicorn

WORKDIR /app

COPY . /app/


RUN pip install --no-cache-dir -r requirements.txt


EXPOSE 8080
