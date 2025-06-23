# Use an official Python runtime as a parent image
FROM python:3.12.11-slim

RUN apt-get update && apt-get install -y \
    pkg-config \
    default-libmysqlclient-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 80

CMD ["streamlit", "run", "main.py", "--server.port", "80", "--server.address", "0.0.0.0"]